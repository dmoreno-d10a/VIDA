"""Administración de usuarios (HU-5, RF-11 a RF-16).

Todas las rutas de este archivo exigen el rol Administrador por la misma
dependencia. No hay ninguna que se proteja por su cuenta, para que no haya
dónde equivocarse (RF-05, RF-11).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.bd import obtener_sesion_bd
from app.esquemas.usuarios import (
    CambioDeAcceso,
    CambioDeRol,
    ContrasenaRestablecida,
    NuevoUsuario,
    UsuarioEnListado,
)
from app.modelos.usuario import Usuario
from app.seguridad.autorizacion import exigir_administrador
from app.seguridad.sesiones import terminar_sesiones_de_usuario
from app.seguridad.contrasena import ErrorDePolitica, calcular_hash_validado

enrutador = APIRouter(
    prefix="/usuarios",
    tags=["usuarios"],
    # Una sola vez, para todas las rutas del archivo.
    dependencies=[Depends(exigir_administrador)],
)

BD = Annotated[Session, Depends(obtener_sesion_bd)]


@enrutador.get("", response_model=list[UsuarioEnListado])
def listar(sesion_bd: BD) -> list[Usuario]:
    """Lista los usuarios con su rol y el estado de su acceso (RF-11)."""
    return list(
        sesion_bd.scalars(select(Usuario).order_by(Usuario.identificacion)).all()
    )


@enrutador.post("", response_model=UsuarioEnListado, status_code=status.HTTP_201_CREATED)
def crear(nuevo: NuevoUsuario, sesion_bd: BD) -> Usuario:
    """Crea un usuario con su rol y su contraseña inicial (RF-12)."""
    ya_existe = sesion_bd.scalar(
        select(Usuario).where(Usuario.identificacion == nuevo.identificacion)
    )
    if ya_existe is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un usuario con esa identificación.",
        )

    try:
        hash_contrasena = calcular_hash_validado(
            nuevo.contrasena, identificacion=nuevo.identificacion
        )
    except ErrorDePolitica as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
        ) from error

    usuario = Usuario(
        identificacion=nuevo.identificacion,
        hash_contrasena=hash_contrasena,
        rol=nuevo.rol,
        activo=True,
    )
    sesion_bd.add(usuario)
    sesion_bd.commit()
    sesion_bd.refresh(usuario)
    return usuario


def _buscar(sesion_bd: Session, usuario_id: int) -> Usuario:
    """Devuelve el usuario o responde que no se encontró."""
    usuario = sesion_bd.get(Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró ese usuario.",
        )
    return usuario


@enrutador.patch("/{usuario_id}/rol", response_model=UsuarioEnListado)
def cambiar_rol(usuario_id: int, cambio: CambioDeRol, sesion_bd: BD) -> Usuario:
    """Cambia el rol de un usuario existente (RF-13).

    No hay que recrear la cuenta, y el cambio aplica de inmediato porque el
    rol se lee de la base en cada petición.
    """
    usuario = _buscar(sesion_bd, usuario_id)
    usuario.rol = cambio.rol
    sesion_bd.commit()
    sesion_bd.refresh(usuario)
    return usuario


@enrutador.post(
    "/{usuario_id}/restablecer-contrasena", status_code=status.HTTP_204_NO_CONTENT
)
def restablecer_contrasena(
    usuario_id: int, restablecimiento: ContrasenaRestablecida, sesion_bd: BD
) -> None:
    """Define una contraseña nueva para un usuario (RF-14).

    La anterior deja de servir, y las sesiones que tuviera abiertas se
    cierran: si se restableció por sospecha, dejarlas abiertas no tendría
    sentido.
    """
    usuario = _buscar(sesion_bd, usuario_id)

    try:
        usuario.hash_contrasena = calcular_hash_validado(
            restablecimiento.contrasena,
            identificacion=usuario.identificacion,
            hash_anterior=usuario.hash_contrasena,
        )
    except ErrorDePolitica as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
        ) from error

    terminar_sesiones_de_usuario(sesion_bd, usuario.id)
    sesion_bd.commit()


@enrutador.patch("/{usuario_id}/acceso", response_model=UsuarioEnListado)
def cambiar_acceso(
    usuario_id: int, cambio: CambioDeAcceso, sesion_bd: BD
) -> Usuario:
    """Revoca o devuelve el acceso de un usuario (RF-15).

    Revocar no borra la cuenta, y corta de inmediato lo que tuviera abierto.
    """
    usuario = _buscar(sesion_bd, usuario_id)
    usuario.activo = cambio.activo

    if not cambio.activo:
        terminar_sesiones_de_usuario(sesion_bd, usuario.id)

    sesion_bd.commit()
    sesion_bd.refresh(usuario)
    return usuario


@enrutador.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(usuario_id: int, sesion_bd: BD) -> None:
    """Elimina un usuario (RF-15). Sus sesiones se van con él."""
    usuario = _buscar(sesion_bd, usuario_id)
    terminar_sesiones_de_usuario(sesion_bd, usuario.id)
    sesion_bd.delete(usuario)
    sesion_bd.commit()
