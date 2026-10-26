"""Pruebas de entrada, salida y bloqueo (HU-1, HU-3, RF-09, RF-22).

Escritas antes de construir: fijan el contrato que debe cumplir el backend.

Lo que estas pruebas protegen, además de que el acceso funcione, es que los
fallos no cuenten de más: la identificación inexistente, la contraseña
incorrecta, la cuenta revocada y la cuenta bloqueada responden **lo mismo**.
La única excepción es el usuario cuyas credenciales son correctas y no tiene
rol: a ese se le indica que solicite autorización, porque ya acreditó quién es
(RF-06, RF-09).
"""

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.configuracion import obtener_configuracion
from tests import datos_ficticios as fic

ENTRAR = "/acceso/entrar"
SALIR = "/acceso/salir"
SESION_ACTUAL = "/acceso/sesion-actual"
COOKIE_SESION = "vida_sesion"


def _entrar(cliente: TestClient, identificacion: str, contrasena: str):
    return cliente.post(
        ENTRAR, json={"identificacion": identificacion, "contrasena": contrasena}
    )


# --- HU-1: entrar a la plataforma -------------------------------------------


def test_el_ro_entra_con_sus_credenciales(cliente: TestClient, usuarios) -> None:
    respuesta = _entrar(cliente, fic.RO.identificacion, fic.RO.contrasena)

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["identificacion"] == fic.RO.identificacion
    assert cuerpo["rol"] == "RO"
    assert COOKIE_SESION in respuesta.cookies


def test_el_administrador_entra_y_el_sistema_lo_reconoce_con_su_rol(
    cliente: TestClient, usuarios
) -> None:
    respuesta = _entrar(
        cliente, fic.ADMINISTRADOR.identificacion, fic.ADMINISTRADOR.contrasena
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["rol"] == "ADMINISTRADOR"


def test_la_cookie_de_sesion_no_es_accesible_desde_javascript(
    cliente: TestClient, usuarios
) -> None:
    """La sesión va en una cookie httpOnly: el front no la manipula (Art. IV)."""
    respuesta = _entrar(cliente, fic.RO.identificacion, fic.RO.contrasena)

    cabecera = respuesta.headers["set-cookie"].lower()
    assert "httponly" in cabecera
    assert "samesite" in cabecera


def test_la_sesion_actual_devuelve_identificacion_y_rol(
    cliente: TestClient, usuarios
) -> None:
    """HU-4: el usuario debe poder ver siempre quién es y con qué rol entró."""
    _entrar(cliente, fic.RO.identificacion, fic.RO.contrasena)

    respuesta = cliente.get(SESION_ACTUAL)

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "identificacion": fic.RO.identificacion,
        "rol": "RO",
    }


def test_al_cerrar_sesion_queda_sin_acceso(cliente: TestClient, usuarios) -> None:
    _entrar(cliente, fic.RO.identificacion, fic.RO.contrasena)

    salida = cliente.post(SALIR)

    assert salida.status_code == 204
    assert cliente.get(SESION_ACTUAL).status_code == 401


def test_sin_haber_entrado_no_hay_sesion_actual(cliente: TestClient) -> None:
    assert cliente.get(SESION_ACTUAL).status_code == 401


# --- HU-3 y RF-09: lo que los fallos no deben contar ------------------------


def _mensaje(respuesta) -> str:
    return respuesta.json()["detalle"]


def test_los_cuatro_fallos_responden_exactamente_lo_mismo(
    cliente: TestClient, usuarios
) -> None:
    """Identificación inexistente, contraseña mala, revocado y bloqueado.

    Si alguno respondiera distinto, se podría averiguar qué identificaciones
    existen en la plataforma (RF-09).
    """
    configuracion = obtener_configuracion()

    inexistente = _entrar(cliente, fic.INEXISTENTE, fic.CONTRASENA_EQUIVOCADA)
    contrasena_mala = _entrar(
        cliente, fic.RO.identificacion, fic.CONTRASENA_EQUIVOCADA
    )
    revocado = _entrar(cliente, fic.REVOCADO.identificacion, fic.REVOCADO.contrasena)

    # Bloqueo: se agotan los intentos de una cuenta que sí existe.
    for _ in range(configuracion.intentos_max):
        _entrar(cliente, fic.SEGUNDO_ADMINISTRADOR.identificacion, "mal-" * 4)
    bloqueado = _entrar(
        cliente,
        fic.SEGUNDO_ADMINISTRADOR.identificacion,
        fic.SEGUNDO_ADMINISTRADOR.contrasena,
    )

    respuestas = [inexistente, contrasena_mala, revocado, bloqueado]

    assert {r.status_code for r in respuestas} == {401}
    assert len({_mensaje(r) for r in respuestas}) == 1, (
        "Los cuatro fallos deben responder el mismo mensaje; si no, se puede "
        "distinguir una cuenta existente de una inexistente."
    )
    for respuesta in respuestas:
        assert COOKIE_SESION not in respuesta.cookies


def test_el_mensaje_de_fallo_no_nombra_la_causa(cliente: TestClient, usuarios) -> None:
    mensaje = _mensaje(
        _entrar(cliente, fic.RO.identificacion, fic.CONTRASENA_EQUIVOCADA)
    ).lower()

    for palabra_delatora in (
        "no existe",
        "inexistente",
        "bloquead",
        "revocad",
        "incorrecta",
        "contraseña",
    ):
        assert palabra_delatora not in mensaje, (
            f"El mensaje de fallo no debe mencionar «{palabra_delatora}»: "
            f"delata qué pasó. Mensaje recibido: {mensaje!r}"
        )


def test_el_usuario_sin_rol_recibe_la_indicacion_de_solicitar_autorizacion(
    cliente: TestClient, usuarios
) -> None:
    """RF-06: acreditó su identidad, así que se le puede decir qué le falta."""
    respuesta = _entrar(cliente, fic.SIN_ROL.identificacion, fic.SIN_ROL.contrasena)

    assert respuesta.status_code == 403
    assert "autorizaci" in _mensaje(respuesta).lower()
    assert COOKIE_SESION not in respuesta.cookies

    # Y además no entra: no hay sesión que consultar.
    assert cliente.get(SESION_ACTUAL).status_code == 401


def test_el_usuario_con_acceso_revocado_no_entra(
    cliente: TestClient, usuarios
) -> None:
    respuesta = _entrar(cliente, fic.REVOCADO.identificacion, fic.REVOCADO.contrasena)

    assert respuesta.status_code == 401
    assert cliente.get(SESION_ACTUAL).status_code == 401


def test_la_sesion_vencida_se_trata_como_sin_acceso(
    cliente: TestClient, usuarios, sesion_bd: Session
) -> None:
    from datetime import UTC, datetime, timedelta

    from app.modelos.sesion import SesionUsuario

    _entrar(cliente, fic.RO.identificacion, fic.RO.contrasena)
    assert cliente.get(SESION_ACTUAL).status_code == 200

    # Se envejece la sesión más allá de la duración configurada.
    sesion_guardada = sesion_bd.query(SesionUsuario).one()
    sesion_guardada.expira_en = datetime.now(UTC) - timedelta(minutes=1)
    sesion_bd.flush()

    assert cliente.get(SESION_ACTUAL).status_code == 401


# --- RF-22: bloqueo por intentos fallidos -----------------------------------


def test_la_cuenta_se_bloquea_al_agotar_los_intentos_configurados(
    cliente: TestClient, usuarios
) -> None:
    configuracion = obtener_configuracion()

    for intento in range(configuracion.intentos_max):
        respuesta = _entrar(
            cliente, fic.RO.identificacion, fic.CONTRASENA_EQUIVOCADA
        )
        assert respuesta.status_code == 401, f"intento {intento + 1}"

    # Con la contraseña correcta tampoco entra: la cuenta quedó bloqueada.
    assert _entrar(cliente, fic.RO.identificacion, fic.RO.contrasena).status_code == 401


def test_un_acceso_correcto_reinicia_el_contador_de_intentos(
    cliente: TestClient, usuarios
) -> None:
    configuracion = obtener_configuracion()

    for _ in range(configuracion.intentos_max - 1):
        _entrar(cliente, fic.RO.identificacion, fic.CONTRASENA_EQUIVOCADA)

    assert _entrar(cliente, fic.RO.identificacion, fic.RO.contrasena).status_code == 200

    # Tras entrar bien, vuelve a disponer de todos los intentos.
    for _ in range(configuracion.intentos_max - 1):
        _entrar(cliente, fic.RO.identificacion, fic.CONTRASENA_EQUIVOCADA)
    assert _entrar(cliente, fic.RO.identificacion, fic.RO.contrasena).status_code == 200


def test_el_bloqueo_se_levanta_por_tiempo_sin_intervencion(
    cliente: TestClient, usuarios, sesion_bd: Session
) -> None:
    """RF-22: el bloqueo es temporal; nadie tiene que desbloquear a mano."""
    from datetime import UTC, datetime, timedelta

    from app.modelos.usuario import Usuario

    configuracion = obtener_configuracion()
    for _ in range(configuracion.intentos_max):
        _entrar(cliente, fic.RO.identificacion, fic.CONTRASENA_EQUIVOCADA)
    assert _entrar(cliente, fic.RO.identificacion, fic.RO.contrasena).status_code == 401

    # Se envejece el bloqueo más allá de su duración configurada.
    usuario = (
        sesion_bd.query(Usuario)
        .filter(Usuario.identificacion == fic.RO.identificacion)
        .one()
    )
    usuario.bloqueado_hasta = datetime.now(UTC) - timedelta(minutes=1)
    sesion_bd.flush()

    assert _entrar(cliente, fic.RO.identificacion, fic.RO.contrasena).status_code == 200
