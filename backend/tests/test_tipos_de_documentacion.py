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
