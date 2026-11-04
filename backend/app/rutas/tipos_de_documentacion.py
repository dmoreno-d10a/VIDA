"""Administración de los tipos de documentación (HU-1 a HU-4).

Todas las rutas de este archivo exigen el rol Administrador por **una sola
dependencia**, puesta en el enrutador. Es la decisión de la 001: ninguna ruta
se protege por su cuenta, para que no haya dónde equivocarse.

Lo que un RO alcanza está en `tipos_disponibles.py`, que es un enrutador
aparte. Separarlos —en vez de filtrar dentro de la misma ruta— es lo que hace
que la protección no dependa de un `if` dentro de una función.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.bd import obtener_sesion_bd
from app.esquemas.tipos_de_documentacion import (
    NuevoTipo,
    TipoEnListado,
)
from app.modelos.tipo_documentacion import TipoDocumentacion
from app.seguridad.autorizacion import exigir_administrador

enrutador = APIRouter(
    prefix="/tipos-de-documentacion",
    tags=["tipos de documentación"],
    dependencies=[Depends(exigir_administrador)],
)

BD = Annotated[Session, Depends(obtener_sesion_bd)]

NOMBRE_REPETIDO = "Ya existe un tipo de documentación con ese nombre."
NO_EXISTE = "No existe ese tipo de documentación."


def _nombre_normalizado(columna):
    """La expresión con la que se comparan dos nombres (RF-02a).

    Es la misma que usa el índice único de la migración. Vive en una función
    para que no puedan separarse: si la consulta comparara de otra forma que
    el índice, el `409` y el error de la base de datos no coincidirían, y una
    de las dos vías dejaría pasar lo que la otra rechaza.

    Los acentos **no** se normalizan: «Factura» y «Fáctura» son tipos
    distintos, porque quitar acentos es decidir por el Administrador qué quiso
    escribir.
    """
    return func.lower(func.trim(columna))


def _existe_otro_con_el_nombre(
    sesion_bd: Session, nombre: str, excepto_id: int | None = None
) -> bool:
    """Si ya hay un tipo con ese nombre, comparado como lo compara el índice."""
    consulta = select(TipoDocumentacion.id).where(
        _nombre_normalizado(TipoDocumentacion.nombre)
        == _nombre_normalizado(func.cast(nombre, TipoDocumentacion.nombre.type))
    )
    if excepto_id is not None:
        consulta = consulta.where(TipoDocumentacion.id != excepto_id)
    return sesion_bd.scalar(consulta) is not None


def _buscar(sesion_bd: Session, tipo_id: int) -> TipoDocumentacion:
    """Devuelve el tipo o responde que no existe."""
    tipo = sesion_bd.get(TipoDocumentacion, tipo_id)
    if tipo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=NO_EXISTE
        )
    return tipo


@enrutador.get("", response_model=list[TipoEnListado])
def listar(sesion_bd: BD) -> list[TipoDocumentacion]:
    """Lista todos los tipos con su estado (RF-03).

    Ordenados por nombre, sin importar su estado: el Administrador ve también
    los incompletos y los desactivados, que es justo lo que un RO no ve.
    """
    return list(
        sesion_bd.scalars(
            select(TipoDocumentacion).order_by(TipoDocumentacion.nombre)
        ).all()
    )


@enrutador.post("", response_model=TipoEnListado, status_code=status.HTTP_201_CREATED)
def crear(nuevo: NuevoTipo, sesion_bd: BD) -> TipoDocumentacion:
    """Crea un tipo, que nace incompleto (RF-01, RF-02).

    Nace sin formato y por lo tanto incompleto: ningún RO lo ve hasta que se
    le cargue uno (RF-16, RF-19).
    """
    if _existe_otro_con_el_nombre(sesion_bd, nuevo.nombre):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=NOMBRE_REPETIDO
        )

    tipo = TipoDocumentacion(nombre=nuevo.nombre, descripcion=nuevo.descripcion)
    sesion_bd.add(tipo)
    sesion_bd.commit()
    sesion_bd.refresh(tipo)
    return tipo
