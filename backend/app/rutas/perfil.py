"""Perfil del propio usuario: cambiar su contraseña (HU-6, RF-17, RF-21).

Esta ruta actúa **solo** sobre quien tiene la sesión: no recibe ningún
identificador de usuario, así que no hay forma de apuntarla a la cuenta de
otro. Cambiar la contraseña es decisión del usuario, no una obligación: el
sistema no la vence por tiempo ni la exige al primer ingreso (RF-21).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.bd import obtener_sesion_bd
from app.esquemas.acceso import CambioDeContrasenaPropia
from app.seguridad.autorizacion import UsuarioAutenticado
from app.seguridad.contrasena import (
    ErrorDePolitica,
    calcular_hash_validado,
    verificar,
)

enrutador = APIRouter(prefix="/perfil", tags=["perfil"])

BD = Annotated[Session, Depends(obtener_sesion_bd)]


@enrutador.patch("/contrasena", status_code=status.HTTP_204_NO_CONTENT)
def cambiar_contrasena(
    cambio: CambioDeContrasenaPropia,
    sesion_bd: BD,
    usuario: UsuarioAutenticado,
) -> None:
    """Cambia la contraseña del usuario de la sesión, acreditando la actual."""
    if not verificar(cambio.contrasena_actual, usuario.hash_contrasena):
        # Mismo trato que un acceso fallido: no se dice qué falló.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar la contraseña actual.",
        )

    try:
        usuario.hash_contrasena = calcular_hash_validado(
            cambio.contrasena_nueva,
            identificacion=usuario.identificacion,
            hash_anterior=usuario.hash_contrasena,
        )
    except ErrorDePolitica as error:
        # Aquí sí se dice qué regla incumplió: es su propia contraseña y
        # necesita saber qué corregir. No se revela nada de otras cuentas.
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
        ) from error

    sesion_bd.commit()
