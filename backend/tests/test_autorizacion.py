"""Pruebas de autorización por rol (HU-2, RF-01, RF-04, RF-05, RF-06).

Lo que estas pruebas protegen es la decisión central del plan: **la
autorización se decide en el backend**, no ocultando opciones en el front. Un
RO que escribe a mano la dirección de una ruta de administración debe
chocarse igual, y sin recibir ni un dato de lo que hay detrás.
"""

import pytest
from fastapi.testclient import TestClient

from tests import datos_ficticios as fic

ENTRAR = "/acceso/entrar"

# Rutas que solo puede usar el rol Administrador (RF-11 a RF-16).
RUTAS_DE_ADMINISTRACION = [
    ("get", "/usuarios"),
    ("post", "/usuarios"),
    ("patch", "/usuarios/1/rol"),
    ("post", "/usuarios/1/restablecer-contrasena"),
    ("patch", "/usuarios/1/acceso"),
    ("delete", "/usuarios/1"),
]

# Rutas que requieren sesión, sin importar el rol.
RUTAS_AUTENTICADAS = [
    ("get", "/acceso/sesion-actual"),
    ("patch", "/perfil/contrasena"),
    *RUTAS_DE_ADMINISTRACION,
]


def _entrar(cliente: TestClient, usuario) -> None:
    respuesta = cliente.post(
        ENTRAR,
        json={
            "identificacion": usuario.identificacion,
            "contrasena": usuario.contrasena,
        },
    )
    assert respuesta.status_code == 200, "el usuario de prueba debería poder entrar"


def _pedir(cliente: TestClient, metodo: str, ruta: str):
    return cliente.request(metodo.upper(), ruta, json={})


# --- RF-01: sin sesión no hay nada ------------------------------------------


@pytest.mark.parametrize(("metodo", "ruta"), RUTAS_AUTENTICADAS)
def test_sin_sesion_ninguna_ruta_entrega_datos(
    cliente: TestClient, metodo: str, ruta: str
) -> None:
    respuesta = _pedir(cliente, metodo, ruta)

    assert respuesta.status_code == 401, f"{metodo.upper()} {ruta} respondió sin sesión"


# --- HU-2 y RF-05: el rol decide, y lo decide el backend --------------------


@pytest.mark.parametrize(("metodo", "ruta"), RUTAS_DE_ADMINISTRACION)
def test_un_ro_no_alcanza_ninguna_ruta_de_administracion(
    cliente: TestClient, usuarios, metodo: str, ruta: str
) -> None:
    """Acceso directo, sin pasar por el menú: el front no es la barrera."""
    _entrar(cliente, fic.RO)

    respuesta = _pedir(cliente, metodo, ruta)

    assert respuesta.status_code == 403, (
        f"{metodo.upper()} {ruta} debería negarse a un RO"
    )


@pytest.mark.parametrize(("metodo", "ruta"), RUTAS_DE_ADMINISTRACION)
def test_al_negar_no_se_filtra_ningun_dato_de_usuarios(
    cliente: TestClient, usuarios, metodo: str, ruta: str
) -> None:
    """RF-05: negar no es responder a medias."""
    _entrar(cliente, fic.RO)

    cuerpo = _pedir(cliente, metodo, ruta).text

    for identificacion in (u.identificacion for u in fic.TODOS):
        assert identificacion not in cuerpo
    for campo in ("hash", "contrasena", "rol"):
        assert campo not in cuerpo.lower()


def test_el_administrador_si_alcanza_la_administracion(
    cliente: TestClient, usuarios
) -> None:
    _entrar(cliente, fic.ADMINISTRADOR)

    assert cliente.get("/usuarios").status_code == 200


def test_el_administrador_tambien_hace_lo_del_ro(
    cliente: TestClient, usuarios
) -> None:
    """RF-04: el rol Administrador incluye todas las opciones del rol RO."""
    _entrar(cliente, fic.ADMINISTRADOR)

    assert cliente.get("/acceso/sesion-actual").status_code == 200


def test_el_rol_se_lee_en_cada_peticion_y_el_cambio_aplica_de_inmediato(
    cliente: TestClient, usuarios, sesion_bd
) -> None:
    """Decisión abierta del plan, resuelta aquí: el cambio de rol no espera."""
    from app.modelos.usuario import Rol, Usuario

    _entrar(cliente, fic.RO)
    assert cliente.get("/usuarios").status_code == 403

    usuario = (
        sesion_bd.query(Usuario)
        .filter(Usuario.identificacion == fic.RO.identificacion)
        .one()
    )
    usuario.rol = Rol.ADMINISTRADOR
    sesion_bd.flush()

    assert cliente.get("/usuarios").status_code == 200, (
        "el rol debe leerse de la base en cada petición, no quedarse fijo en la sesión"
    )


def test_al_revocar_el_acceso_la_sesion_abierta_deja_de_servir(
    cliente: TestClient, usuarios, sesion_bd
) -> None:
    """RF-15: revocar no puede esperar a que la sesión expire."""
    from app.modelos.usuario import Usuario

    _entrar(cliente, fic.RO)
    assert cliente.get("/acceso/sesion-actual").status_code == 200

    usuario = (
        sesion_bd.query(Usuario)
        .filter(Usuario.identificacion == fic.RO.identificacion)
        .one()
    )
    usuario.activo = False
    sesion_bd.flush()

    assert cliente.get("/acceso/sesion-actual").status_code == 401


def test_quitarle_el_rol_a_un_usuario_con_sesion_lo_deja_sin_acceso(
    cliente: TestClient, usuarios, sesion_bd
) -> None:
    """RF-06: sin rol no hay acceso, tampoco a mitad de una sesión."""
    from app.modelos.usuario import Usuario

    _entrar(cliente, fic.RO)

    usuario = (
        sesion_bd.query(Usuario)
        .filter(Usuario.identificacion == fic.RO.identificacion)
        .one()
    )
    usuario.rol = None
    sesion_bd.flush()

    assert cliente.get("/acceso/sesion-actual").status_code in (401, 403)


def test_la_ruta_de_salud_no_exige_sesion(cliente: TestClient) -> None:
    """Única excepción deliberada: sirve para saber si el backend está arriba."""
    assert cliente.get("/salud").status_code == 200
