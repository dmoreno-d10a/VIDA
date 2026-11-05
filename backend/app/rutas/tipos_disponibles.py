"""Los tipos de documentación que un RO puede elegir (HU-5, RF-16).

Es lo único de esta funcionalidad que un RO alcanza, y exige **solo sesión**:
cualquier rol, porque el Administrador también documenta.

**Por qué un enrutador aparte y no un filtro en el de administración.** El
enrutador de administración niega el paso a los RO de una sola vez, en su
dependencia. Si la misma ruta sirviera a los dos roles con un filtro, la
protección pasaría a depender de un `if` dentro de la función, y ahí es donde
se cometen los errores que la 001 decidió hacer imposibles.

Lo que esta ruta devuelve es `id`, `nombre` y `descripcion`, y nada más. No
expone estructura, historial, versiones, tipos incompletos ni desactivados:
no por filtrarlos, sino porque el esquema no los tiene y la consulta no los
pide.
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.bd import obtener_sesion_bd
from app.esquemas.tipos_de_documentacion import TipoDisponible
from app.modelos.tipo_documentacion import TipoDocumentacion
from app.seguridad.autorizacion import usuario_actual

enrutador = APIRouter(
    prefix="/tipos-de-documentacion-disponibles",
    tags=["tipos de documentación"],
    # Solo sesión. A diferencia del enrutador de administración, aquí no se
    # exige rol: un RO es justamente a quien sirve esta ruta.
    dependencies=[Depends(usuario_actual)],
)

BD = Annotated[Session, Depends(obtener_sesion_bd)]


@enrutador.get("", response_model=list[TipoDisponible])
def listar_disponibles(sesion_bd: BD) -> list[TipoDocumentacion]:
    """Los tipos activos, ordenados por nombre (RF-16).

    «Activo» es tener una versión vigente y no estar desactivado, que es la
    misma definición derivada del modelo, escrita aquí como condición de la
    consulta para que la base no traiga lo que no se va a mostrar.

    Devuelve `[]` cuando no hay ninguno. Convertir eso en el mensaje explícito
    que pide HU-5 es del front: una lista vacía es una respuesta, no un error.
    """
    return list(
        sesion_bd.scalars(
            select(TipoDocumentacion)
            .where(
                TipoDocumentacion.version_vigente_id.is_not(None),
                TipoDocumentacion.desactivado.is_(False),
            )
            .order_by(TipoDocumentacion.nombre)
        ).all()
    )
