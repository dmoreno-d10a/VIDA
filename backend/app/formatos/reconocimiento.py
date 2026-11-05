"""Puerta única de la carga de un formato.

Todo archivo que carga el Administrador pasa por aquí: tamaño, extensión,
firma, y una lectura de la estructura que es **una pista y no un juez**.

**Un formato nunca se rechaza por su estructura.** Si la lectura no reconoce
secciones ni columnas, el archivo se acepta igual y la estructura queda vacía.
El formato es la referencia con la que después se llena el documento, y la IA
que lo llena trabaja sobre el archivo original, que se guarda intacto: decidir
al cargarlo que un archivo «no sirve» porque no marcó sus títulos como Word
espera es adelantarse a un problema que no es de quien carga.

Lo que sí se rechaza es lo que no es un formato: un archivo sobre el límite,
una extensión que no se admite, un `.doc` viejo renombrado a `.docx`, y uno
que no se puede abrir. Ese último se rechaza aquí a propósito, aunque no sea
un juicio sobre la estructura: un archivo dañado o protegido con contraseña no
lo va a poder llenar nadie, y descubrirlo al cargarlo es mucho más amable que
descubrirlo cuando un RO ya documentó una actividad.

**Las tres barreras van antes de abrir nada**, y en ese orden a propósito:
rechazar por tamaño es una comparación de enteros, rechazar por extensión es
una comparación de cadenas, y comprobar la firma son cuatro bytes. Abrir el
archivo es lo caro, así que es lo último.

La lectura ocurre **una sola vez, al cargar** (Art. VI). Lo que se reconozca
se guarda con la versión, y ni el detalle del tipo ni las funcionalidades
posteriores vuelven a abrir el archivo para saber qué hay dentro.
"""

import logging
from dataclasses import dataclass

from app.configuracion import obtener_configuracion
from app.formatos import lector_excel, lector_word

registro = logging.getLogger(__name__)

# Los cuatro bytes con los que empieza todo archivo ZIP, y `.docx`/`.xlsx` lo
# son. Es lo que distingue un documento de Office actual de un `.doc` de los
# viejos al que solo le cambiaron el nombre.
FIRMA_ZIP = b"PK\x03\x04"


class ErrorDeFormato(Exception):
    """Base de los rechazos de un formato. Cada subclase es un código del contrato."""


class ArchivoDemasiadoGrande(ErrorDeFormato):
    """Supera el tamaño máximo configurado → `413` (RF-18)."""


class ExtensionNoAdmitida(ErrorDeFormato):
    """La extensión o la firma no corresponden a Office actual → `415` (RF-04)."""


class ArchivoIlegible(ErrorDeFormato):
    """Dañado, protegido o no se pudo abrir → `422` (RF-10).

    Es el **único** rechazo que ocurre después de abrir el archivo, y no es un
    juicio sobre su estructura: es que no hay archivo con el que trabajar.
    """


@dataclass(frozen=True)
class FormatoReconocido:
    """Lo que la puerta devuelve. Siempre, si el archivo se pudo abrir."""

    extension: str

    estructura: dict
    """Lo que se reconoció, que **puede estar vacío**.

    Vacío no es un error: es «este formato no marca sus secciones de una forma
    que se pueda leer sin interpretar», y la estructura es una pista para que
    la 004 sepa por dónde empezar a preguntar, no la definición del documento.
    """


_LECTORES = {"docx": lector_word, "xlsx": lector_excel}


def extension_de(nombre_archivo: str) -> str:
    """La extensión del nombre, en minúsculas y sin punto."""
    _, _, extension = nombre_archivo.rpartition(".")
    return extension.lower()


def reconocer(contenido: bytes, nombre_archivo: str) -> FormatoReconocido:
    """Valida el archivo y lee lo que se pueda, o levanta un `ErrorDeFormato`."""
    configuracion = obtener_configuracion()

    # --- Barrera 1: tamaño (RF-18) ---
    if len(contenido) > configuracion.formato_tamano_max_bytes:
        raise ArchivoDemasiadoGrande(
            f"El archivo supera el tamaño máximo permitido "
            f"({configuracion.formato_mb_max} MB)."
        )

    # --- Barrera 2: extensión (RF-04) ---
    extension = extension_de(nombre_archivo)
    if extension not in configuracion.extensiones_admitidas:
        raise ExtensionNoAdmitida(_mensaje_de_extension(configuracion))

    # --- Barrera 3: firma ---
    # Un `.doc` renombrado pasa la barrera de la extensión y muere aquí.
    if not contenido.startswith(FIRMA_ZIP):
        raise ExtensionNoAdmitida(_mensaje_de_extension(configuracion))

    lector = _LECTORES.get(extension)
    if lector is None:
        # La configuración admite una extensión para la que no hay lector. Es
        # un error de instalación, no del archivo, pero el Administrador no
        # puede hacer nada distinto: se le responde lo mismo que al 415.
        registro.error(
            "La extensión %r está admitida en la configuración pero no tiene lector.",
            extension,
        )
        raise ExtensionNoAdmitida(_mensaje_de_extension(configuracion))

    # --- La lectura, que informa pero no decide ---
    try:
        estructura = lector.leer(contenido)
    except lector.ErrorDeLectura as error:
        raise ArchivoIlegible(
            "No se pudo leer el archivo. Puede estar dañado o protegido con "
            "contraseña."
        ) from error

    if lector.sin_estructura(estructura):
        # Se registra porque es útil saber cuántos formatos del área caen aquí
        # —de eso depende cuánto trabajo tendrá la 004—, pero no cambia nada:
        # el formato se acepta.
        registro.info(
            "No se reconoció estructura en un %s; se acepta igual y la "
            "estructura queda vacía.",
            extension,
        )

    return FormatoReconocido(extension=extension, estructura=estructura)


def _mensaje_de_extension(configuracion) -> str:
    """El mensaje del `415`, que nombra las extensiones admitidas (RF-04).

    Se arma desde la configuración y no se escribe a mano: si alguien agrega
    una extensión admitida, el mensaje no puede quedarse diciendo otra cosa.
    """
    nombres = {"docx": "Word (.docx)", "xlsx": "Excel (.xlsx)"}
    admitidas = [
        nombres.get(extension, f".{extension}")
        for extension in configuracion.extensiones_admitidas
    ]
    if len(admitidas) > 1:
        listado = " y ".join([", ".join(admitidas[:-1]), admitidas[-1]])
    else:
        listado = admitidas[0] if admitidas else "ninguno"
    return f"Solo se admiten formatos de {listado}."
