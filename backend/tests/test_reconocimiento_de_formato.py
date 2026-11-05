"""Pruebas del reconocimiento de la estructura de un formato (HU-2).

La prueba central compara la estructura reconocida contra la que **exporta el
generador** (T009), no contra una lista escrita aquí. Esa diferencia es lo que
hace del Art. II algo verificable: si el reconocimiento agregara, renombrara o
reordenara algo, la comparación falla, y no depende de que a quien escribe la
prueba se le ocurra el caso.

Los tres formatos con estilos cubren el Art. VIII: dos de ellos son ajenos al
caso de referencia, y uno es de otra clase de archivo.
"""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tests import datos_ficticios as fic

TIPOS = "/tipos-de-documentacion"


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


def _cargar(cliente: TestClient, tipo_id: int, ruta: Path, nombre: str | None = None):
    return cliente.post(
        f"{TIPOS}/{tipo_id}/formato",
        files={"archivo": (nombre or ruta.name, ruta.read_bytes())},
    )


def _cargar_bytes(cliente: TestClient, tipo_id: int, contenido: bytes, nombre: str):
    return cliente.post(
        f"{TIPOS}/{tipo_id}/formato", files={"archivo": (nombre, contenido)}
    )


# --- RF-05, RF-17, CE-01, CE-04: la estructura es la del archivo ------------


@pytest.mark.parametrize(
    "clave",
    ["referencia", "generalizacion_word", "generalizacion_excel"],
)
def test_la_estructura_reconocida_es_identica_a_la_del_archivo(
    cliente: TestClient,
    usuarios,
    almacen_temporal,
    formatos_de_prueba,
    estructuras_esperadas,
    clave: str,
) -> None:
    """Cero elementos agregados, renombrados, eliminados o reordenados (Art. I)."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, f"Tipo de {clave}")

    respuesta = _cargar(cliente, tipo_id, formatos_de_prueba[clave])

    assert respuesta.status_code == 201
    assert respuesta.json()["estructura"] == estructuras_esperadas[clave]


def test_el_tipo_pasa_a_activo_al_cargar_el_formato(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    """RF-19: con una versión vigente, el tipo deja de estar incompleto."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Adapter Reverso")

    assert _cargar(
        cliente, tipo_id, formatos_de_prueba["referencia"]
    ).status_code == 201

    fila = next(f for f in cliente.get(TIPOS).json() if f["id"] == tipo_id)
    assert fila["estado"] == "activo"
    assert fila["version_vigente"]["numero"] == 1


def test_la_primera_version_es_la_numero_uno(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Adapter Reverso")

    respuesta = _cargar(cliente, tipo_id, formatos_de_prueba["referencia"])

    assert respuesta.json()["numero"] == 1


def test_el_nombre_original_del_archivo_se_conserva(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    """RF-20: el Administrador tiene que reconocer cuál cargó."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Adapter Reverso")

    respuesta = _cargar(
        cliente,
        tipo_id,
        formatos_de_prueba["referencia"],
        nombre="formato con acentos y espacios.docx",
    )

    assert respuesta.json()["nombre_archivo_original"] == (
        "formato con acentos y espacios.docx"
    )


# --- RF-11, RF-06: los casos borde de la sección 7 --------------------------


def test_un_titulo_sin_texto_se_registra_como_nulo(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    """RF-11: no se le inventa un nombre."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Con título vacío")

    estructura = _cargar(
        cliente, tipo_id, formatos_de_prueba["generalizacion_word"]
    ).json()["estructura"]

    sin_nombre = [s for s in estructura["secciones"] if s["nombre"] is None]
    assert len(sin_nombre) == 1


def test_dos_titulos_con_el_mismo_nombre_aparecen_los_dos(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    """RF-06: no se fusionan ni se renumeran."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Con nombres repetidos")

    estructura = _cargar(
        cliente, tipo_id, formatos_de_prueba["generalizacion_word"]
    ).json()["estructura"]

    repetidos = [s for s in estructura["secciones"] if s["nombre"] == "Detalle"]
    assert len(repetidos) == 2


def test_dos_columnas_con_el_mismo_nombre_se_conservan(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Excel con columnas repetidas")

    estructura = _cargar(
        cliente, tipo_id, formatos_de_prueba["generalizacion_excel"]
    ).json()["estructura"]

    request = next(h for h in estructura["hojas"] if h["nombre"] == "Request")
    assert request["columnas"].count("Campo") == 2


def test_los_encabezados_salen_de_la_fila_que_los_tiene(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    """RF-05b: la hoja «Response» los trae en la fila 3, bajo un título."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Excel con título arriba")

    estructura = _cargar(
        cliente, tipo_id, formatos_de_prueba["generalizacion_excel"]
    ).json()["estructura"]

    response = next(h for h in estructura["hojas"] if h["nombre"] == "Response")
    assert response["fila_de_encabezados"] == 3
    assert response["columnas"] == ["Campo", "Tipo", "Descripción"]


def test_una_hoja_sin_encabezados_es_valida(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    """Lo que no es válido es un libro sin **ninguna** columna."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Excel con hoja vacía")

    estructura = _cargar(
        cliente, tipo_id, formatos_de_prueba["generalizacion_excel"]
    ).json()["estructura"]

    notas = next(h for h in estructura["hojas"] if h["nombre"] == "Notas")
    assert notas["columnas"] == []
    assert notas["fila_de_encabezados"] is None


# --- RF-10, RF-18, CE-06: los cuatro rechazos -------------------------------


def _estado_de(cliente: TestClient, tipo_id: int) -> str:
    return next(f for f in cliente.get(TIPOS).json() if f["id"] == tipo_id)["estado"]


def test_una_extension_no_admitida_se_rechaza_con_415(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Con PDF")

    respuesta = _cargar(
        cliente, tipo_id, formatos_de_prueba["referencia"], nombre="formato.pdf"
    )

    assert respuesta.status_code == 415
    assert ".docx" in respuesta.json()["detalle"]
    assert ".xlsx" in respuesta.json()["detalle"]
    assert _estado_de(cliente, tipo_id) == "incompleto"


def test_un_doc_renombrado_a_docx_se_rechaza_con_415(
    cliente: TestClient, usuarios, almacen_temporal
) -> None:
    """La extensión no basta: lo atrapa la firma del archivo."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Con doc viejo")

    # La firma de un `.doc` de los viejos (OLE2), no la de un ZIP.
    respuesta = _cargar_bytes(
        cliente, tipo_id, b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" + b"x" * 500, "viejo.docx"
    )

    assert respuesta.status_code == 415
    assert _estado_de(cliente, tipo_id) == "incompleto"


def test_un_archivo_sobre_el_limite_se_rechaza_con_413(
    cliente: TestClient, usuarios, almacen_temporal, monkeypatch
) -> None:
    """RF-18: el techo es configurable, así que la prueba lo baja."""
    from app.configuracion import obtener_configuracion

    monkeypatch.setenv("VIDA_FORMATO_MB_MAX", "1")
    obtener_configuracion.cache_clear()

    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Con archivo grande")

    respuesta = _cargar_bytes(
        cliente, tipo_id, b"PK\x03\x04" + b"x" * (2 * 1024 * 1024), "grande.docx"
    )

    assert respuesta.status_code == 413
    assert "1 MB" in respuesta.json()["detalle"]
    assert _estado_de(cliente, tipo_id) == "incompleto"


def test_un_archivo_danado_se_rechaza_con_su_propio_mensaje(
    cliente: TestClient, usuarios, almacen_temporal
) -> None:
    """RF-10: «no se pudo leer» no es lo mismo que «no tiene estructura»."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Con archivo dañado")

    # Empieza como un ZIP, así que pasa la firma, pero no es un `.docx`.
    respuesta = _cargar_bytes(
        cliente, tipo_id, b"PK\x03\x04" + b"basura" * 50, "roto.docx"
    )

    assert respuesta.status_code == 422
    assert "dañado o protegido" in respuesta.json()["detalle"]
    assert _estado_de(cliente, tipo_id) == "incompleto"


def test_un_word_sin_estructura_se_acepta_igual(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    """Un formato nunca se rechaza por su estructura (RF-10).

    `solo-negritas.docx` marca sus secciones con negrita, que es algo que una
    persona reconoce y `python-docx` no. El archivo se acepta, el tipo queda
    activo y la estructura queda vacía: el formato es la referencia con la que
    después se llena el documento, y el archivo original se guarda intacto.
    """
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Solo negritas")

    respuesta = _cargar(cliente, tipo_id, formatos_de_prueba["solo_negritas"])

    assert respuesta.status_code == 201
    assert respuesta.json()["estructura"] == {"clase": "word", "secciones": []}
    assert _estado_de(cliente, tipo_id) == "activo"


def test_un_excel_sin_un_solo_encabezado_se_acepta_igual(
    cliente: TestClient, usuarios, almacen_temporal
) -> None:
    """La misma regla en la rama de Excel."""
    from io import BytesIO

    from openpyxl import Workbook

    libro = Workbook()
    libro.active.title = "Vacía"
    memoria = BytesIO()
    libro.save(memoria)

    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Excel sin encabezados")

    respuesta = _cargar_bytes(
        cliente, tipo_id, memoria.getvalue(), "sin-encabezados.xlsx"
    )

    assert respuesta.status_code == 201
    assert respuesta.json()["estructura"]["hojas"][0]["columnas"] == []
    assert _estado_de(cliente, tipo_id) == "activo"


def test_el_archivo_se_guarda_intacto_aunque_no_se_reconozca_nada(
    cliente: TestClient, usuarios, sesion_bd, almacen_temporal, formatos_de_prueba
) -> None:
    """Lo que de verdad importa: el original queda byte por byte.

    Es lo que permite que la IA lo llene después sin cambiarle el estilo, y
    no depende de que la lectura haya reconocido algo.
    """
    import hashlib

    from sqlalchemy import select

    from app.formatos import almacen
    from app.modelos.tipo_documentacion import FormatoVersion

    original = formatos_de_prueba["solo_negritas"].read_bytes()

    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Intacto")
    assert _cargar(
        cliente, tipo_id, formatos_de_prueba["solo_negritas"]
    ).status_code == 201

    version = sesion_bd.scalar(
        select(FormatoVersion).where(FormatoVersion.tipo_id == tipo_id)
    )
    assert almacen.leer(version.ruta_almacenada) == original
    assert version.hash_sha256 == hashlib.sha256(original).hexdigest()


def test_cargar_a_un_tipo_que_no_existe_responde_404(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)

    respuesta = _cargar(cliente, 99999, formatos_de_prueba["referencia"])

    assert respuesta.status_code == 404


def test_un_ro_no_puede_cargar_un_formato(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    _entrar(cliente, fic.RO)

    assert _cargar(cliente, 1, formatos_de_prueba["referencia"]).status_code == 403


# --- RF-13, RF-21: reemplazar crea una versión nueva ------------------------


def test_reemplazar_el_formato_crea_la_version_dos(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Adapter Reverso")

    assert _cargar(
        cliente, tipo_id, formatos_de_prueba["referencia"]
    ).json()["numero"] == 1
    segunda = _cargar(cliente, tipo_id, formatos_de_prueba["generalizacion_word"])

    assert segunda.status_code == 201
    assert segunda.json()["numero"] == 2

    fila = next(f for f in cliente.get(TIPOS).json() if f["id"] == tipo_id)
    assert fila["version_vigente"]["numero"] == 2


def test_reemplazar_por_un_archivo_invalido_deja_el_formato_anterior(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    """RF-10: en el rechazo el tipo conserva su versión vigente."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Adapter Reverso")
    assert _cargar(
        cliente, tipo_id, formatos_de_prueba["referencia"]
    ).status_code == 201

    assert _cargar_bytes(
        cliente, tipo_id, b"PK\x03\x04basura", "roto.docx"
    ).status_code == 422

    fila = next(f for f in cliente.get(TIPOS).json() if f["id"] == tipo_id)
    assert fila["estado"] == "activo"
    assert fila["version_vigente"]["numero"] == 1


# --- RF-07, CE-03, Art. VI: el formato se analiza una sola vez --------------


def test_consultar_el_detalle_no_vuelve_a_analizar_el_archivo(
    cliente: TestClient,
    usuarios,
    almacen_temporal,
    formatos_de_prueba,
    monkeypatch,
) -> None:
    """RF-07: la estructura sale de la base de datos, no del archivo.

    Se verifica de forma **observable** y no leyendo el código: se cuentan las
    veces que se abre un lector. Si el detalle volviera a analizar, el
    contador subiría, y con el respaldo con IA eso costaría además una
    consulta al modelo por cada vez que alguien abre la pantalla.
    """
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Adapter Reverso")
    assert _cargar(
        cliente, tipo_id, formatos_de_prueba["referencia"]
    ).status_code == 201

    from app.formatos import lector_word

    lecturas: list[int] = []
    leer_de_verdad = lector_word.leer

    def leer_contando(contenido: bytes):
        lecturas.append(len(contenido))
        return leer_de_verdad(contenido)

    monkeypatch.setattr(lector_word, "leer", leer_contando)

    primera = cliente.get(f"{TIPOS}/{tipo_id}")
    segunda = cliente.get(f"{TIPOS}/{tipo_id}")

    assert primera.status_code == segunda.status_code == 200
    assert primera.json()["version_vigente"]["estructura"] == (
        segunda.json()["version_vigente"]["estructura"]
    )
    assert lecturas == []


def test_el_historial_va_de_la_mas_nueva_a_la_mas_vieja(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    """RF-21, y la vigente queda marcada."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Adapter Reverso")
    for clave in ("referencia", "generalizacion_word", "generalizacion_excel"):
        assert _cargar(cliente, tipo_id, formatos_de_prueba[clave]).status_code == 201

    detalle = cliente.get(f"{TIPOS}/{tipo_id}").json()

    assert [v["numero"] for v in detalle["historial"]] == [3, 2, 1]
    assert [v["vigente"] for v in detalle["historial"]] == [True, False, False]


def test_el_detalle_no_trae_la_estructura_de_las_versiones_anteriores(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    """Si viniera, el detalle de un tipo con muchas versiones no tendría techo."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Adapter Reverso")
    _cargar(cliente, tipo_id, formatos_de_prueba["referencia"])
    _cargar(cliente, tipo_id, formatos_de_prueba["generalizacion_word"])

    detalle = cliente.get(f"{TIPOS}/{tipo_id}").json()

    assert all("estructura" not in v for v in detalle["historial"])


def test_la_estructura_de_una_version_anterior_se_pide_por_su_ruta(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba,
    estructuras_esperadas,
) -> None:
    """RF-21: el reemplazo no pierde lo que había antes."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Adapter Reverso")
    _cargar(cliente, tipo_id, formatos_de_prueba["referencia"])
    _cargar(cliente, tipo_id, formatos_de_prueba["generalizacion_word"])

    primera = cliente.get(f"{TIPOS}/{tipo_id}/formato/versiones/1")

    assert primera.status_code == 200
    assert primera.json()["estructura"] == estructuras_esperadas["referencia"]


def test_una_version_que_no_existe_responde_404(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear_tipo(cliente, "Adapter Reverso")
    _cargar(cliente, tipo_id, formatos_de_prueba["referencia"])

    assert cliente.get(f"{TIPOS}/{tipo_id}/formato/versiones/7").status_code == 404


def test_el_detalle_de_un_tipo_que_no_existe_responde_404(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)

    respuesta = cliente.get(f"{TIPOS}/99999")

    assert respuesta.status_code == 404
    assert respuesta.json()["detalle"] == "No existe ese tipo de documentación."
