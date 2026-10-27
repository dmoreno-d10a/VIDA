"""Sesiones: crear, validar y terminar.

Una sesión válida exige tres cosas al mismo tiempo, y se comprueban en cada
petición: que la sesión no haya expirado, que el usuario siga activo y que
siga teniendo rol. Si cualquiera falla, no hay acceso (RF-01, RF-06, RF-15).
"""

import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.configuracion import obtener_configuracion
from app.modelos.sesion import SesionUsuario
from app.modelos.usuario import Usuario

# Nombre de la cookie que lleva el identificador opaco de la sesión.
COOKIE_SESION = "vida_sesion"

# Bytes de aleatoriedad del identificador. 32 bytes son 64 caracteres en
# hexadecimal, que es el largo de la columna.
_BYTES_DEL_IDENTIFICADOR = 32


def _ahora() -> datetime:
    return datetime.now(UTC)


def crear_sesion(sesion_bd: Session, usuario: Usuario) -> SesionUsuario:
    """Abre una sesión para el usuario, con la duración configurada (RF-07)."""
    configuracion = obtener_configuracion()
    sesion = SesionUsuario(
        id=secrets.token_hex(_BYTES_DEL_IDENTIFICADOR),
        usuario_id=usuario.id,
        expira_en=_ahora() + timedelta(minutes=configuracion.sesion_minutos),
    )
    sesion_bd.add(sesion)
    sesion_bd.flush()
    return sesion


def usuario_de_la_sesion(
    sesion_bd: Session, identificador: str | None
) -> Usuario | None:
    """Devuelve el usuario de una sesión válida, o `None`.

    Devuelve `None` tanto si la sesión no existe o venció, como si el usuario
    quedó revocado o sin rol: desde el punto de vista del acceso, los cuatro
    casos son lo mismo.
    """
    if not identificador:
        return None

    sesion = sesion_bd.get(SesionUsuario, identificador)
    if sesion is None:
        return None

    if _expiro(sesion):
        terminar_sesion(sesion_bd, identificador)
        return None

    usuario = sesion.usuario
    if usuario is None or not usuario.activo or usuario.rol is None:
        return None

    return usuario


def _expiro(sesion: SesionUsuario) -> bool:
    """Indica si la sesión ya venció, comparando siempre en UTC."""
    expira_en = sesion.expira_en
    if expira_en.tzinfo is None:
        expira_en = expira_en.replace(tzinfo=UTC)
    return expira_en <= _ahora()


def terminar_sesion(sesion_bd: Session, identificador: str | None) -> None:
    """Cierra una sesión. No falla si ya no existe."""
    if not identificador:
        return
    sesion = sesion_bd.get(SesionUsuario, identificador)
    if sesion is not None:
        sesion_bd.delete(sesion)
        sesion_bd.flush()


def duracion_en_segundos() -> int:
    """Duración configurada de la sesión, para la cookie."""
    return obtener_configuracion().sesion_minutos * 60


def terminar_sesiones_de_usuario(sesion_bd: Session, usuario_id: int) -> int:
    """Cierra todas las sesiones abiertas de un usuario.

    Se usa al cerrar sesión, al revocar o eliminar la cuenta y al restablecer
    la contraseña: en todos esos casos lo ya abierto deja de servir (RF-15).
    """
    from app.modelos.sesion import terminar_sesiones_de

    terminadas = terminar_sesiones_de(sesion_bd, usuario_id)
    sesion_bd.flush()
    return terminadas
