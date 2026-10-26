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
from app.esquemas.usuarios import NuevoUsuario, UsuarioEnListado
from app.modelos.usuario import Usuario
from app.seguridad.autorizacion import exigir_administrador
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
