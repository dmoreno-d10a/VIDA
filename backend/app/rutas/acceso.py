"""Rutas de acceso: entrar, cerrar sesión y consultar la sesión actual.

El cuidado de este archivo está en lo que **no** dice. Identificación
inexistente, contraseña incorrecta, cuenta revocada y cuenta bloqueada
responden exactamente lo mismo, para que nadie pueda averiguar qué
identificaciones existen en la plataforma (RF-09).

La única excepción es el usuario cuyas credenciales son correctas y no tiene
rol: a ese se le indica que solicite autorización, porque ya acreditó quién es
(RF-06).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.bd import obtener_sesion_bd
from app.esquemas.acceso import SesionActual, SolicitudDeAcceso
from app.modelos.usuario import Usuario
from app.seguridad import sesiones
from app.seguridad.autorizacion import UsuarioAutenticado, usuario_actual
from app.seguridad.contrasena import verificar
from app.seguridad.sesiones import COOKIE_SESION

enrutador = APIRouter(prefix="/acceso", tags=["acceso"])

# Un único mensaje para los cuatro fallos. No nombra la causa ni el dato que
# falló: si lo hiciera, se podría distinguir una cuenta existente de una que
# no existe (RF-09).
NO_SE_PUDO_VALIDAR = "No se pudo validar el acceso. Revisa los datos ingresados."

SOLICITA_AUTORIZACION = (
    "Tu cuenta no tiene acceso asignado todavía. Solicita autorización al "
    "administrador de la plataforma."
)

BD = Annotated[Session, Depends(obtener_sesion_bd)]


def _acceso_negado() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail=NO_SE_PUDO_VALIDAR
    )


@enrutador.post("/entrar", response_model=SesionActual)
def entrar(
    solicitud: SolicitudDeAcceso, respuesta: Response, sesion_bd: BD
) -> Usuario:
    """Abre una sesión si las credenciales son correctas (HU-1)."""
    usuario = sesion_bd.scalar(
        select(Usuario).where(Usuario.identificacion == solicitud.identificacion)
    )

    # Usuario inexistente: se responde igual que con contraseña incorrecta.
    if usuario is None:
        raise _acceso_negado()

    if _esta_bloqueado(usuario):
        raise _acceso_negado()

    if not verificar(solicitud.contrasena, usuario.hash_contrasena):
        _contar_intento_fallido(usuario, sesion_bd)
        raise _acceso_negado()

    # Desde aquí, la contraseña es correcta: el usuario acreditó su identidad.
    _reiniciar_intentos(usuario, sesion_bd)

    if not usuario.activo:
        raise _acceso_negado()

    if usuario.rol is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=SOLICITA_AUTORIZACION
        )

    sesion = sesiones.crear_sesion(sesion_bd, usuario)
    respuesta.set_cookie(
        key=COOKIE_SESION,
        value=sesion.id,
        max_age=sesiones.duracion_en_segundos(),
        httponly=True,
        samesite="lax",
        path="/",
    )
    return usuario


@enrutador.post("/salir", status_code=status.HTTP_204_NO_CONTENT)
def salir(
    respuesta: Response,
    sesion_bd: BD,
    usuario: UsuarioAutenticado,
) -> None:
    """Cierra la sesión y borra la cookie (HU-1)."""
    sesiones.terminar_sesiones_de_usuario(sesion_bd, usuario.id)
    respuesta.delete_cookie(COOKIE_SESION, path="/")


@enrutador.get("/sesion-actual", response_model=SesionActual)
def sesion_actual(usuario: Annotated[Usuario, Depends(usuario_actual)]) -> Usuario:
    """Devuelve identificación y rol vigente del usuario (HU-4, RF-08)."""
    return usuario


# --- Intentos fallidos y bloqueo (RF-22, se completa en T021) --------------


def _esta_bloqueado(usuario: Usuario) -> bool:
    """Por ahora nunca bloquea: el bloqueo se implementa en T021."""
    return False


def _contar_intento_fallido(usuario: Usuario, sesion_bd: Session) -> None:
    """Por ahora no cuenta: el conteo se implementa en T021."""
    return None


def _reiniciar_intentos(usuario: Usuario, sesion_bd: Session) -> None:
    """Por ahora no hay contador que reiniciar: se implementa en T021."""
    return None
