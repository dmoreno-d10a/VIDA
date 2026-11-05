"""Pruebas de la creación y el listado de tipos de documentación (HU-1).

Lo que se verifica aquí, además de que la ruta funcione:

- Que el nombre se guarde **tal como se escribió** pero se compare sin
  mayúsculas ni espacios de sobra, y que los acentos sí distingan (RF-02a).
  Es la regla que más fácil se implementa a medias.
- Que un tipo nuevo nazca `incompleto` y no `activo`: un tipo sin formato no
  puede llegarle a un RO (RF-16, RF-19).
- Que un RO no alcance ninguna de estas rutas, ni escribiendo la dirección.
"""

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


def _crear(cliente: TestClient, nombre: str, descripcion: str | None = None):
    cuerpo: dict[str, object] = {"nombre": nombre}
    if descripcion is not None:
        cuerpo["descripcion"] = descripcion
    return cliente.post(TIPOS, json=cuerpo)


# --- RF-01, RF-02: crear ----------------------------------------------------


def test_un_tipo_nuevo_nace_incompleto(cliente: TestClient, usuarios) -> None:
    """Sin formato no hay tipo utilizable, y el estado lo dice (RF-19)."""
    _entrar(cliente, fic.ADMINISTRADOR)

    respuesta = _crear(cliente, "Adapter Reverso", "Adapters de reverso")

    assert respuesta.status_code == 201
    creado = respuesta.json()
    assert creado["nombre"] == "Adapter Reverso"
    assert creado["descripcion"] == "Adapters de reverso"
    assert creado["estado"] == "incompleto"
    assert creado["version_vigente"] is None


def test_la_descripcion_puede_faltar(cliente: TestClient, usuarios) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)

    respuesta = _crear(cliente, "Servicio nuevo")

    assert respuesta.status_code == 201
    assert respuesta.json()["descripcion"] is None


def test_la_descripcion_de_solo_espacios_queda_como_ausente(
    cliente: TestClient, usuarios
) -> None:
    """«Sin descripción» es un solo estado, no dos que se ven igual."""
    _entrar(cliente, fic.ADMINISTRADOR)

    respuesta = _crear(cliente, "Servicio nuevo", "   ")

    assert respuesta.status_code == 201
    assert respuesta.json()["descripcion"] is None


def test_el_nombre_se_guarda_tal_como_se_escribio(
    cliente: TestClient, usuarios
) -> None:
    """El dato del usuario no se normaliza (Art. II)."""
    _entrar(cliente, fic.ADMINISTRADOR)

    respuesta = _crear(cliente, "  Adapter   REVERSO  ")

    assert respuesta.status_code == 201
    assert respuesta.json()["nombre"] == "  Adapter   REVERSO  "


def test_el_nombre_vacio_se_rechaza(cliente: TestClient, usuarios) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)

    assert _crear(cliente, "").status_code == 422


def test_el_nombre_de_solo_espacios_se_rechaza(
    cliente: TestClient, usuarios
) -> None:
    """RF-02a: no vacío **tras quitar espacios**."""
    _entrar(cliente, fic.ADMINISTRADOR)

    respuesta = _crear(cliente, "     ")

    assert respuesta.status_code == 422


def test_el_nombre_mas_largo_que_el_maximo_se_rechaza(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)

    assert _crear(cliente, "a" * 200).status_code == 201
    assert _crear(cliente, "b" * 201).status_code == 422


def test_la_descripcion_mas_larga_que_el_maximo_se_rechaza(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)

    assert _crear(cliente, "Con descripción larga", "d" * 1001).status_code == 422


# --- RF-02a: cómo se comparan dos nombres -----------------------------------


def test_el_nombre_repetido_se_rechaza(cliente: TestClient, usuarios) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    assert _crear(cliente, "Adapter Reverso").status_code == 201

    respuesta = _crear(cliente, "Adapter Reverso")

    assert respuesta.status_code == 409
    assert "ya existe" in respuesta.json()["detalle"].lower()


def test_el_mismo_nombre_con_otras_mayusculas_se_rechaza(
    cliente: TestClient, usuarios
) -> None:
    """Para el Administrador son el mismo tipo (RF-02a)."""
    _entrar(cliente, fic.ADMINISTRADOR)
    assert _crear(cliente, "Adapter Reverso").status_code == 201

    assert _crear(cliente, "adapter reverso").status_code == 409


def test_el_mismo_nombre_con_espacios_de_sobra_se_rechaza(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    assert _crear(cliente, "Adapter Reverso").status_code == 201

    assert _crear(cliente, "  Adapter Reverso  ").status_code == 409


def test_los_acentos_distinguen_dos_tipos(cliente: TestClient, usuarios) -> None:
    """Quitar acentos sería decidir por el Administrador qué quiso escribir."""
    _entrar(cliente, fic.ADMINISTRADOR)
    assert _crear(cliente, "Factura").status_code == 201

    assert _crear(cliente, "Fáctura").status_code == 201


# --- RF-03: listar ----------------------------------------------------------


def test_el_listado_va_ordenado_por_nombre(cliente: TestClient, usuarios) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    for nombre in ("Zeta", "Alfa", "Media"):
        assert _crear(cliente, nombre).status_code == 201

    listado = cliente.get(TIPOS).json()

    assert [fila["nombre"] for fila in listado] == ["Alfa", "Media", "Zeta"]


def test_el_listado_muestra_el_estado_de_cada_tipo(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    assert _crear(cliente, "Sin formato").status_code == 201

    listado = cliente.get(TIPOS).json()

    assert listado[0]["estado"] == "incompleto"
    assert listado[0]["version_vigente"] is None


def test_el_listado_vacio_es_una_lista_vacia(cliente: TestClient, usuarios) -> None:
    """No un 404: «no hay tipos» es una respuesta, no un error."""
    _entrar(cliente, fic.ADMINISTRADOR)

    respuesta = cliente.get(TIPOS)

    assert respuesta.status_code == 200
    assert respuesta.json() == []


# --- Art. X.1: solo el Administrador ----------------------------------------


def test_un_ro_no_alcanza_el_listado(cliente: TestClient, usuarios) -> None:
    """La barrera está en el enrutador, no en el front (Art. IV)."""
    _entrar(cliente, fic.RO)

    assert cliente.get(TIPOS).status_code == 403


def test_un_ro_no_puede_crear_un_tipo(cliente: TestClient, usuarios) -> None:
    _entrar(cliente, fic.RO)

    assert _crear(cliente, "Creado por un RO").status_code == 403


def test_sin_sesion_no_se_alcanza_nada(cliente: TestClient, usuarios) -> None:
    assert cliente.get(TIPOS).status_code == 401
    assert _crear(cliente, "Sin sesión").status_code == 401


# --- RF-12: modificar -------------------------------------------------------


def _detalle(cliente: TestClient, tipo_id: int) -> dict:
    respuesta = cliente.get(f"{TIPOS}/{tipo_id}")
    assert respuesta.status_code == 200
    return respuesta.json()


def _cargar_referencia(cliente: TestClient, tipo_id: int, formatos) -> None:
    respuesta = cliente.post(
        f"{TIPOS}/{tipo_id}/formato",
        files={
            "archivo": (
                formatos["referencia"].name,
                formatos["referencia"].read_bytes(),
            )
        },
    )
    assert respuesta.status_code == 201


def test_se_puede_cambiar_el_nombre_y_la_descripcion(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear(cliente, "Nombre viejo", "Descripción vieja").json()["id"]

    respuesta = cliente.patch(
        f"{TIPOS}/{tipo_id}",
        json={"nombre": "Nombre nuevo", "descripcion": "Descripción nueva"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Nombre nuevo"
    assert respuesta.json()["descripcion"] == "Descripción nueva"


def test_se_puede_cambiar_solo_la_descripcion(cliente: TestClient, usuarios) -> None:
    """Los dos campos son opcionales: se cambia lo que venga."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear(cliente, "Nombre que no cambia", "Vieja").json()["id"]

    respuesta = cliente.patch(f"{TIPOS}/{tipo_id}", json={"descripcion": "Nueva"})

    assert respuesta.json()["nombre"] == "Nombre que no cambia"
    assert respuesta.json()["descripcion"] == "Nueva"


def test_se_puede_quitar_la_descripcion(cliente: TestClient, usuarios) -> None:
    """Mandar `null` es distinto de no mandar el campo."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear(cliente, "Con descripción", "La tenía").json()["id"]

    respuesta = cliente.patch(f"{TIPOS}/{tipo_id}", json={"descripcion": None})

    assert respuesta.json()["descripcion"] is None


def test_renombrar_a_un_nombre_ya_tomado_se_rechaza(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    assert _crear(cliente, "Adapter Reverso").status_code == 201
    otro_id = _crear(cliente, "Factura").json()["id"]

    respuesta = cliente.patch(f"{TIPOS}/{otro_id}", json={"nombre": "adapter reverso"})

    assert respuesta.status_code == 409
    assert respuesta.json()["detalle"] == (
        "Ya existe un tipo de documentación con ese nombre."
    )


def test_renombrar_un_tipo_con_su_propio_nombre_no_choca_consigo_mismo(
    cliente: TestClient, usuarios
) -> None:
    """El choque se busca **excepto** en el propio tipo."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear(cliente, "Adapter Reverso").json()["id"]

    respuesta = cliente.patch(f"{TIPOS}/{tipo_id}", json={"nombre": "Adapter Reverso"})

    assert respuesta.status_code == 200


def test_modificar_no_toca_la_estructura_reconocida(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    """RF-12: el formato no cambió, así que no se vuelve a analizar."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear(cliente, "Adapter Reverso").json()["id"]
    _cargar_referencia(cliente, tipo_id, formatos_de_prueba)
    antes = _detalle(cliente, tipo_id)["version_vigente"]

    cliente.patch(f"{TIPOS}/{tipo_id}", json={"nombre": "Adapter de reverso"})

    assert _detalle(cliente, tipo_id)["version_vigente"] == antes


# --- RF-14: desactivar y reactivar ------------------------------------------


def test_se_puede_desactivar_y_reactivar_un_tipo(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear(cliente, "Adapter Reverso").json()["id"]
    _cargar_referencia(cliente, tipo_id, formatos_de_prueba)

    desactivado = cliente.post(
        f"{TIPOS}/{tipo_id}/activacion", json={"desactivado": True}
    )
    assert desactivado.status_code == 200
    assert desactivado.json()["estado"] == "desactivado"

    reactivado = cliente.post(
        f"{TIPOS}/{tipo_id}/activacion", json={"desactivado": False}
    )
    assert reactivado.json()["estado"] == "activo"


def test_desactivar_no_pierde_el_formato(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    """Desactivar es sacar de circulación, no borrar."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear(cliente, "Adapter Reverso").json()["id"]
    _cargar_referencia(cliente, tipo_id, formatos_de_prueba)

    cliente.post(f"{TIPOS}/{tipo_id}/activacion", json={"desactivado": True})

    assert _detalle(cliente, tipo_id)["version_vigente"]["numero"] == 1


def test_activar_un_tipo_incompleto_se_rechaza(cliente: TestClient, usuarios) -> None:
    """«Activo» no es escribible: se deriva de tener una versión vigente."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear(cliente, "Sin formato").json()["id"]

    respuesta = cliente.post(
        f"{TIPOS}/{tipo_id}/activacion", json={"desactivado": False}
    )

    assert respuesta.status_code == 409
    assert "no tiene un formato cargado" in respuesta.json()["detalle"]


def test_desactivar_un_tipo_incompleto_si_se_permite(
    cliente: TestClient, usuarios
) -> None:
    """Es sacar de la lista del Administrador algo que creó por error."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear(cliente, "Creado por error").json()["id"]

    respuesta = cliente.post(
        f"{TIPOS}/{tipo_id}/activacion", json={"desactivado": True}
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "desactivado"


# --- RF-15, RF-15a: eliminar ------------------------------------------------


def test_se_puede_eliminar_un_tipo_incompleto(cliente: TestClient, usuarios) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear(cliente, "Creado por error").json()["id"]

    assert cliente.delete(f"{TIPOS}/{tipo_id}").status_code == 204
    assert cliente.get(f"{TIPOS}/{tipo_id}").status_code == 404


def test_eliminar_un_tipo_con_formato_se_rechaza_y_ofrece_desactivarlo(
    cliente: TestClient, usuarios, almacen_temporal, formatos_de_prueba
) -> None:
    """RF-15: el mensaje ofrece la alternativa en la misma frase."""
    _entrar(cliente, fic.ADMINISTRADOR)
    tipo_id = _crear(cliente, "Adapter Reverso").json()["id"]
    _cargar_referencia(cliente, tipo_id, formatos_de_prueba)

    respuesta = cliente.delete(f"{TIPOS}/{tipo_id}")

    assert respuesta.status_code == 409
    assert "desactivarlo" in respuesta.json()["detalle"]
    # Y sigue ahí.
    assert cliente.get(f"{TIPOS}/{tipo_id}").status_code == 200


def test_eliminar_un_tipo_que_no_existe_responde_404(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)

    assert cliente.delete(f"{TIPOS}/99999").status_code == 404


def test_un_ro_no_puede_modificar_activar_ni_eliminar(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.RO)

    assert cliente.patch(f"{TIPOS}/1", json={"nombre": "X"}).status_code == 403
    assert cliente.post(
        f"{TIPOS}/1/activacion", json={"desactivado": True}
    ).status_code == 403
    assert cliente.delete(f"{TIPOS}/1").status_code == 403
