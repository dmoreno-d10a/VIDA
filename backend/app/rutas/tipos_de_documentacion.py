"""Administración de los tipos de documentación (HU-1 a HU-4).

Todas las rutas de este archivo exigen el rol Administrador por **una sola
dependencia**, puesta en el enrutador. Es la decisión de la 001: ninguna ruta
se protege por su cuenta, para que no haya dónde equivocarse.

Lo que un RO alcanza está en `tipos_disponibles.py`, que es un enrutador
aparte. Separarlos —en vez de filtrar dentro de la misma ruta— es lo que hace
que la protección no dependa de un `if` dentro de una función.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError, OperationalError
from sqlalchemy.orm import Session

from app.bd import obtener_sesion_bd
from app.configuracion import obtener_configuracion
from app.esquemas.tipos_de_documentacion import (
    CambioDeActivacion,
    CambioDeTipo,
    DetalleDeTipo,
    NuevoTipo,
    TipoEnListado,
    VersionConEstructura,
)
from app.formatos import almacen, reconocimiento
from app.modelos.tipo_documentacion import FormatoVersion, TipoDocumentacion
from app.seguridad.autorizacion import exigir_administrador

registro = logging.getLogger(__name__)

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


# --- RF-04 a RF-11, RF-13, RF-19: cargar o reemplazar el formato -----------

CARGA_EN_CURSO = (
    "Hay otra carga de formato en curso para este tipo. Intenta de nuevo en un "
    "momento."
)

# Cuánto se lee de la red por vez. El tamaño no es crítico; lo que importa es
# que la lectura sea por trozos y no de una, para poder cortar a tiempo.
TROZO = 64 * 1024


async def _leer_con_techo(archivo: UploadFile, techo_bytes: int) -> bytes:
    """Lee el archivo cortando **en cuanto** pasa el techo (RF-18).

    Se lee por trozos a propósito. Leerlo completo y después medirlo
    significaría recibir 500 MB para responder que no se admiten 26: el
    rechazo tiene que ocurrir mientras llega, no después.
    """
    trozos: list[bytes] = []
    recibido = 0
    while trozo := await archivo.read(TROZO):
        recibido += len(trozo)
        if recibido > techo_bytes:
            raise reconocimiento.ArchivoDemasiadoGrande(
                f"El archivo supera el tamaño máximo permitido "
                f"({obtener_configuracion().formato_mb_max} MB)."
            )
        trozos.append(trozo)
    return b"".join(trozos)


# Cada error del reconocimiento tiene un código del contrato. El mapa está
# aquí y no dentro de un `if`: agregar una clase de rechazo es agregar una
# línea, no otra rama que se puede olvidar.
_CODIGOS = {
    reconocimiento.ArchivoDemasiadoGrande: status.HTTP_413_CONTENT_TOO_LARGE,
    reconocimiento.ExtensionNoAdmitida: status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
    reconocimiento.ArchivoIlegible: status.HTTP_422_UNPROCESSABLE_CONTENT,
}


@enrutador.post(
    "/{tipo_id}/formato",
    response_model=VersionConEstructura,
    status_code=status.HTTP_201_CREATED,
)
async def cargar_formato(
    tipo_id: int,
    sesion_bd: BD,
    archivo: Annotated[UploadFile, File()],
) -> FormatoVersion:
    """Carga o reemplaza el formato de un tipo, creando una versión nueva.

    El orden de este cuerpo es la parte que importa: **leer el archivo,
    guardarlo y reconocerlo pasa antes de abrir la transacción.** Dentro de
    ella no puede haber entrada ni salida de disco ni una espera de red,
    porque sostendría el candado de la fila del tipo durante segundos —y con
    el respaldo con IA, hasta veinte—, bloqueando cualquier otra carga sobre
    el mismo tipo.
    """
    # Que el tipo exista se comprueba antes de leer el archivo: no tiene
    # sentido recibir 25 MB para después decir que el tipo no existe.
    _buscar(sesion_bd, tipo_id)

    configuracion = obtener_configuracion()
    try:
        contenido = await _leer_con_techo(
            archivo, configuracion.formato_tamano_max_bytes
        )
        reconocido = reconocimiento.reconocer(contenido, archivo.filename or "")
    except reconocimiento.ErrorDeFormato as error:
        raise HTTPException(
            status_code=_CODIGOS[type(error)], detail=str(error)
        ) from error

    try:
        guardado = almacen.guardar(contenido, reconocido.extension)
    except almacen.ErrorDeAlmacen as error:
        # El archivo era bueno y la plataforma falló. No es culpa de quien
        # carga, y el mensaje no le echa la culpa.
        registro.error("No se pudo guardar un formato válido: %s", error)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo guardar el archivo. Intenta de nuevo.",
        ) from error

    # --- Desde aquí sí, la transacción, que es corta ---
    try:
        tipo = sesion_bd.scalars(
            select(TipoDocumentacion)
            .where(TipoDocumentacion.id == tipo_id)
            # `nowait`: si otra carga tiene el candado, se responde 409 en vez
            # de dejar la petición esperando sin que nadie sepa por qué.
            .with_for_update(nowait=True)
        ).one_or_none()
    except (OperationalError, DBAPIError) as error:
        sesion_bd.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=CARGA_EN_CURSO
        ) from error

    if tipo is None:
        # Lo eliminaron entre la comprobación de arriba y el candado.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NO_EXISTE)

    ultimo = sesion_bd.scalar(
        select(func.max(FormatoVersion.numero)).where(
            FormatoVersion.tipo_id == tipo_id
        )
    )

    version = FormatoVersion(
        tipo_id=tipo_id,
        numero=(ultimo or 0) + 1,
        nombre_archivo_original=archivo.filename or f"formato.{reconocido.extension}",
        extension=reconocido.extension,
        tamano_bytes=guardado.tamano_bytes,
        hash_sha256=guardado.hash_sha256,
        ruta_almacenada=guardado.ruta_relativa,
        estructura=reconocido.estructura,
    )
    sesion_bd.add(version)
    sesion_bd.flush()

    # Queda vigente de inmediato, venga la estructura de la lectura o de la
    # propuesta de la IA: la base no distingue las dos, y el tipo pasa a
    # activo (RF-19).
    tipo.version_vigente_id = version.id
    sesion_bd.commit()
    sesion_bd.refresh(version)
    return version


# --- RF-07, RF-08, RF-21: el detalle y el historial ------------------------


def _historial_de(tipo: TipoDocumentacion) -> list[dict]:
    """El historial, de la versión más nueva a la más vieja (RF-21)."""
    return [
        {
            "numero": version.numero,
            "nombre_archivo_original": version.nombre_archivo_original,
            "creado_en": version.creado_en,
            "vigente": version.id == tipo.version_vigente_id,
        }
        for version in sorted(tipo.versiones, key=lambda v: v.numero, reverse=True)
    ]


@enrutador.get("/{tipo_id}", response_model=DetalleDeTipo)
def detalle(tipo_id: int, sesion_bd: BD) -> dict:
    """El detalle del tipo, con su estructura vigente y su historial (RF-08).

    La estructura sale de la base de datos: **el archivo no se vuelve a
    abrir** (RF-07, Art. VI). Reabrir esta pantalla no cuesta un análisis, y
    menos una consulta al modelo.
    """
    tipo = _buscar(sesion_bd, tipo_id)
    return {
        "id": tipo.id,
        "nombre": tipo.nombre,
        "descripcion": tipo.descripcion,
        "estado": tipo.estado,
        "version_vigente": tipo.version_vigente,
        "historial": _historial_de(tipo),
    }


@enrutador.get(
    "/{tipo_id}/formato/versiones/{numero}", response_model=VersionConEstructura
)
def version_anterior(tipo_id: int, numero: int, sesion_bd: BD) -> FormatoVersion:
    """La estructura de una versión cualquiera del historial (RF-21).

    Está en su propia ruta y no dentro del detalle para que el detalle de un
    tipo con muchas versiones no crezca sin límite.
    """
    _buscar(sesion_bd, tipo_id)
    version = sesion_bd.scalar(
        select(FormatoVersion).where(
            FormatoVersion.tipo_id == tipo_id, FormatoVersion.numero == numero
        )
    )
    if version is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe esa versión del formato.",
        )
    return version


# --- RF-12, RF-14, RF-15: mantener los tipos -------------------------------

NO_SE_PUEDE_ACTIVAR = (
    "Este tipo no tiene un formato cargado, así que no puede activarse."
)

# El mensaje **ofrece la alternativa** en la misma frase, como pide RF-15: al
# Administrador no le sirve saber solo que no puede, sino qué sí puede hacer.
NO_SE_PUEDE_ELIMINAR = (
    "Este tipo ya tiene un formato cargado y no se puede eliminar. Puedes "
    "desactivarlo para que los RO no lo vean."
)


@enrutador.patch("/{tipo_id}", response_model=TipoEnListado)
def modificar(
    tipo_id: int, cambio: CambioDeTipo, sesion_bd: BD
) -> TipoDocumentacion:
    """Cambia nombre y descripción (RF-12).

    **No toca la estructura reconocida.** Corregir el nombre de un tipo no
    tiene por qué volver a analizar su formato, y el formato no cambió.

    Los dos campos son opcionales: se cambia lo que venga. Un campo ausente y
    un campo en `null` significan distinto para la descripción —no cambiarla,
    o dejarla sin descripción— y `model_fields_set` es lo que los distingue.
    """
    tipo = _buscar(sesion_bd, tipo_id)
    enviados = cambio.model_fields_set

    if "nombre" in enviados and cambio.nombre is not None:
        if _existe_otro_con_el_nombre(sesion_bd, cambio.nombre, excepto_id=tipo_id):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail=NOMBRE_REPETIDO
            )
        tipo.nombre = cambio.nombre

    if "descripcion" in enviados:
        tipo.descripcion = (
            cambio.descripcion
            if cambio.descripcion is None or cambio.descripcion.strip()
            else None
        )

    sesion_bd.commit()
    sesion_bd.refresh(tipo)
    return tipo


@enrutador.post("/{tipo_id}/activacion", response_model=TipoEnListado)
def cambiar_activacion(
    tipo_id: int, cambio: CambioDeActivacion, sesion_bd: BD
) -> TipoDocumentacion:
    """Desactiva un tipo o lo devuelve a circulación (RF-14).

    Es una ruta propia y no parte del `PATCH` porque es una decisión distinta:
    corregir la descripción de un tipo y sacarlo de circulación no se piden en
    el mismo gesto, y separarlas evita desactivar un tipo por accidente al
    renombrarlo.
    """
    tipo = _buscar(sesion_bd, tipo_id)

    if not cambio.desactivado and tipo.version_vigente_id is None:
        # Activar un tipo sin formato dejaría al RO elegir algo que no se
        # puede usar. El estado «activo» no es escribible: se deriva de tener
        # una versión vigente.
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=NO_SE_PUEDE_ACTIVAR
        )

    tipo.desactivado = cambio.desactivado
    sesion_bd.commit()
    sesion_bd.refresh(tipo)
    return tipo


@enrutador.delete("/{tipo_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(tipo_id: int, sesion_bd: BD) -> None:
    """Elimina un tipo que nunca llegó a usarse (RF-15, RF-15a).

    Solo procede sin versión vigente, que es la lectura literal de «tipos que
    nunca han sido usados»: un tipo sin formato vigente nunca pudo ser elegido
    por un RO.
    """
    tipo = _buscar(sesion_bd, tipo_id)

    if tipo.version_vigente_id is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=NO_SE_PUEDE_ELIMINAR
        )

    sesion_bd.delete(tipo)
    sesion_bd.commit()
