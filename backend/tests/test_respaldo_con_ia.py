"""Pruebas del respaldo con IA del reconocimiento (RF-05c, RF-05d).

**Ninguna de estas pruebas sale a la red.** El apoyo `litellm_fijo` sustituye
`propuesta_ia.consultar_litellm`, que es la única función de la funcionalidad
que hace una petición HTTP. Lo que se verifica no es que el modelo acierte
—eso no se puede afirmar en una prueba— sino lo que sí es mecánico:

- que un nombre que el modelo trae y el documento **no** contiene se descarte
  (RF-05d). Esa es la prueba que hace del Art. II algo verificable para este
  camino, y no una confianza;
- que la lectura directa tenga prioridad, contando las llamadas: un formato
  bien marcado no debe costar un solo token (Art. VI);
- que las tres formas de fallar le lleguen al Administrador como una sola.
"""

import json
from pathlib import Path

from fastapi.testclient import TestClient

from tests import datos_ficticios as fic

TIPOS = "/tipos-de-documentacion"

# Los cuatro nombres que `solo-negritas.docx` trae de verdad.
SECCIONES_REALES = ["Contexto", "Entradas", "Salidas", "Validaciones"]


def _entrar(cliente: TestClient, usuario) -> None:
    respuesta = cliente.post(
        "/acceso/entrar",
        json={
            "identificacion": usuario.identificacion,
            "contrasena": usuario.contrasena,
        },
    )
    assert respuesta.status_code == 200


def _crear_tipo(cliente: TestClient, nombre: str) -> int:
    respuesta = cliente.post(TIPOS, json={"nombre": nombre})
    assert respuesta.status_code == 201
    return respuesta.json()["id"]


def _cargar(cliente: TestClient, tipo_id: int, ruta: Path):
    return cliente.post(
        f"{TIPOS}/{tipo_id}/formato", files={"archivo": (ruta.name, ruta.read_bytes())}
    )


def _propuesta_word(nombres: list[str]) -> str:
    return json.dumps(
        {
            "clase": "word",
            "secciones": [{"nombre": n, "nivel": 1} for n in nombres],
        }
    )


def _con_credencial(monkeypatch) -> None:
    """Enciende el respaldo con una credencial ficticia.

    Sin credencial el respaldo se da por indisponible y no se intenta la
    llamada, así que las pruebas del camino tienen que poner una. Es inventada
    y no sirve en ninguna parte (Art. X.2, Art. X.3).
    """
    from app.configuracion import obtener_configuracion

    monkeypatch.setenv("VIDA_IA_RESPALDO", "1")
    monkeypatch.setenv("VIDA_LITELLM_API_KEY", "credencial-ficticia-de-prueba")
    obtener_configuracion.cache_clear()


def _estado_de(cliente: TestClient, tipo_id: int) -> str:
    return next(f for f in cliente.get(TIPOS).json() if f["id"] == tipo_id)["estado"]


# --- RF-05c: el camino del respaldo -----------------------------------------


def test_un_word_sin_estilos_queda_activo_con_la_estructura_propuesta(
    cliente: TestClient,
    usuarios,
    almacen_temporal,
    formatos_de_prueba,
    litellm_fijo,
    monkeypatch,
) -> None:
    """La carga se acepta y el tipo queda activo, como con cualquier formato."""
    _con_credencial(monkeypatch)
    litellm_fijo.respuesta = _propuesta_word(SECCIONES_REALES)

    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Solo negritas")

    respuesta = _cargar(cliente, tipo_id, formatos_de_prueba["solo_negritas"])

    assert respuesta.status_code == 201
    estructura = respuesta.json()["estructura"]
    assert [s["nombre"] for s in estructura["secciones"]] == SECCIONES_REALES
    assert _estado_de(cliente, tipo_id) == "activo"
    assert litellm_fijo.veces == 1


def test_la_respuesta_no_distingue_si_la_estructura_la_propuso_la_ia(
    cliente: TestClient,
    usuarios,
    almacen_temporal,
    formatos_de_prueba,
    litellm_fijo,
    monkeypatch,
) -> None:
    """Una sola forma de respuesta, sin estados intermedios."""
    _con_credencial(monkeypatch)
    litellm_fijo.respuesta = _propuesta_word(SECCIONES_REALES)

    _entrar(cliente, fic.ADMINISTRADOR)
    propuesta = _cargar(
        cliente,
        _crear_tipo(cliente, "Propuesta"),
        formatos_de_prueba["solo_negritas"],
    ).json()
    leida = _cargar(
        cliente, _crear_tipo(cliente, "Leída"), formatos_de_prueba["referencia"]
    ).json()

    assert set(propuesta) == set(leida)
    assert propuesta["numero"] == leida["numero"] == 1


# --- RF-05d, CE-04: el descarte de lo que no está en el documento -----------


def test_un_nombre_que_no_esta_en_el_documento_se_descarta(
    cliente: TestClient,
    usuarios,
    almacen_temporal,
    formatos_de_prueba,
    litellm_fijo,
    monkeypatch,
) -> None:
    """La prueba que hace del Art. II algo verificable en este camino.

    El modelo propone una sección que el documento no tiene. No se guarda, y
    tampoco se reemplaza por otra: lo que no entró, no existió.
    """
    _con_credencial(monkeypatch)
    litellm_fijo.respuesta = _propuesta_word(
        ["Contexto", "Consideraciones de seguridad", "Salidas"]
    )

    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Con un nombre inventado")

    respuesta = _cargar(cliente, tipo_id, formatos_de_prueba["solo_negritas"])

    assert respuesta.status_code == 201
    nombres = [s["nombre"] for s in respuesta.json()["estructura"]["secciones"]]
    assert nombres == ["Contexto", "Salidas"]
    assert "Consideraciones de seguridad" not in nombres


def test_un_nombre_con_otras_mayusculas_tambien_se_descarta(
    cliente: TestClient,
    usuarios,
    almacen_temporal,
    formatos_de_prueba,
    litellm_fijo,
    monkeypatch,
) -> None:
    """«Literalmente» es literal: el nombre va como está en el archivo (Art. I).

    Aceptar «CONTEXTO» por «Contexto» sería dejar que el modelo decida cómo se
    escribe una sección del formato, que es justo lo que el Art. I no admite.
    """
    _con_credencial(monkeypatch)
    litellm_fijo.respuesta = _propuesta_word(["CONTEXTO", "Entradas"])

    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Con mayúsculas cambiadas")

    respuesta = _cargar(cliente, tipo_id, formatos_de_prueba["solo_negritas"])

    nombres = [s["nombre"] for s in respuesta.json()["estructura"]["secciones"]]
    assert nombres == ["Entradas"]


def test_si_tras_el_descarte_no_queda_nada_se_rechaza(
    cliente: TestClient,
    usuarios,
    almacen_temporal,
    formatos_de_prueba,
    litellm_fijo,
    monkeypatch,
) -> None:
    """Una propuesta entera inventada equivale a no tener propuesta."""
    _con_credencial(monkeypatch)
    litellm_fijo.respuesta = _propuesta_word(["Sección inventada", "Otra inventada"])

    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Todo inventado")

    respuesta = _cargar(cliente, tipo_id, formatos_de_prueba["solo_negritas"])

    assert respuesta.status_code == 422
    assert "no se reconoció ninguna estructura" in respuesta.json()["detalle"].lower()
    assert _estado_de(cliente, tipo_id) == "incompleto"


# --- Las tres fallas son una sola para el Administrador ---------------------


def test_el_respaldo_apagado_y_el_cliente_fallando_dan_el_mismo_422(
    cliente: TestClient,
    usuarios,
    almacen_temporal,
    formatos_de_prueba,
    litellm_fijo,
    monkeypatch,
) -> None:
    """Nombrarle una falla de un servicio interno no le da con qué actuar."""
    _con_credencial(monkeypatch)
    litellm_fijo.falla = RuntimeError("LiteLLM no responde")

    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Con el cliente fallando")

    fallando = _cargar(cliente, tipo_id, formatos_de_prueba["solo_negritas"])

    assert fallando.status_code == 422

    # Ahora el mismo archivo con el respaldo apagado.
    from app.configuracion import obtener_configuracion

    monkeypatch.setenv("VIDA_IA_RESPALDO", "0")
    obtener_configuracion.cache_clear()
    apagado = _cargar(
        cliente, _crear_tipo(cliente, "Apagado"), formatos_de_prueba["solo_negritas"]
    )

    assert apagado.status_code == 422
    assert apagado.json()["detalle"] == fallando.json()["detalle"]


def test_sin_credencial_no_se_intenta_la_llamada(
    cliente: TestClient,
    usuarios,
    almacen_temporal,
    formatos_de_prueba,
    litellm_fijo,
    monkeypatch,
) -> None:
    """Sin credencial no hay a quién preguntarle: no se gasta la llamada."""
    from app.configuracion import obtener_configuracion

    monkeypatch.setenv("VIDA_IA_RESPALDO", "1")
    monkeypatch.delenv("VIDA_LITELLM_API_KEY", raising=False)
    obtener_configuracion.cache_clear()

    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Sin credencial")

    respuesta = _cargar(cliente, tipo_id, formatos_de_prueba["solo_negritas"])

    assert respuesta.status_code == 422
    assert litellm_fijo.veces == 0


def test_una_respuesta_que_no_es_json_se_trata_como_sin_propuesta(
    cliente: TestClient,
    usuarios,
    almacen_temporal,
    formatos_de_prueba,
    litellm_fijo,
    monkeypatch,
) -> None:
    _con_credencial(monkeypatch)
    litellm_fijo.respuesta = "Claro, con gusto. El documento parece tener secciones."

    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Respuesta en prosa")

    assert _cargar(
        cliente, tipo_id, formatos_de_prueba["solo_negritas"]
    ).status_code == 422


def test_un_json_envuelto_en_bloque_de_codigo_se_entiende(
    cliente: TestClient,
    usuarios,
    almacen_temporal,
    formatos_de_prueba,
    litellm_fijo,
    monkeypatch,
) -> None:
    """Algunos modelos lo envuelven aunque se les pida que no."""
    _con_credencial(monkeypatch)
    litellm_fijo.respuesta = (
        "```json\n" + _propuesta_word(["Contexto"]) + "\n```"
    )

    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Con bloque de código")

    respuesta = _cargar(cliente, tipo_id, formatos_de_prueba["solo_negritas"])

    assert respuesta.status_code == 201
    assert respuesta.json()["estructura"]["secciones"] == [
        {"nombre": "Contexto", "nivel": 1}
    ]


# --- Art. VI: la lectura directa tiene prioridad ----------------------------


def test_un_formato_con_estilos_no_consulta_el_modelo_ni_una_vez(
    cliente: TestClient,
    usuarios,
    almacen_temporal,
    formatos_de_prueba,
    litellm_fijo,
    monkeypatch,
) -> None:
    """Un formato bien marcado no debe costar un solo token (Art. VI)."""
    _con_credencial(monkeypatch)

    _entrar(cliente, fic.ADMINISTRADOR)
    for clave in ("referencia", "generalizacion_word", "generalizacion_excel"):
        tipo_id = _crear_tipo(cliente, f"Con estilos: {clave}")
        assert _cargar(cliente, tipo_id, formatos_de_prueba[clave]).status_code == 201

    assert litellm_fijo.veces == 0


def test_un_archivo_danado_no_consulta_el_modelo(
    cliente: TestClient, usuarios, almacen_temporal, litellm_fijo, monkeypatch
) -> None:
    """Un archivo que no se pudo abrir no tiene texto que mandar."""
    _con_credencial(monkeypatch)

    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Dañado")

    respuesta = cliente.post(
        f"{TIPOS}/{tipo_id}/formato",
        files={"archivo": ("roto.docx", b"PK\x03\x04" + b"basura" * 50)},
    )

    assert respuesta.status_code == 422
    assert "dañado o protegido" in respuesta.json()["detalle"]
    assert litellm_fijo.veces == 0


def test_a_la_ia_se_le_manda_el_esqueleto_y_no_el_archivo(
    cliente: TestClient,
    usuarios,
    almacen_temporal,
    formatos_de_prueba,
    litellm_fijo,
    monkeypatch,
) -> None:
    """Art. VI: lo que viaja es texto con señales de forma, no el `.docx`."""
    _con_credencial(monkeypatch)
    litellm_fijo.respuesta = _propuesta_word(SECCIONES_REALES)

    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Esqueleto")
    _cargar(cliente, tipo_id, formatos_de_prueba["solo_negritas"])

    mandado = litellm_fijo.llamadas[0]
    assert isinstance(mandado, str)
    # Ni la firma del ZIP ni los nombres internos del paquete `.docx`.
    assert "PK\x03\x04" not in mandado
    assert "word/document.xml" not in mandado
    # Y sí las señales de forma, que es lo que permite reconocer una sección.
    assert "negrita" in mandado
    assert "Contexto" in mandado
    # Más corto que el archivo, por mucho.
    assert len(mandado) < formatos_de_prueba["solo_negritas"].stat().st_size / 10
