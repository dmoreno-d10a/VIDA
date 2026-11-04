"""Puerta única del reconocimiento de un formato.

Todo archivo que carga el Administrador pasa por aquí, y por aquí en este
orden: tamaño, extensión, firma, lectura, y solo entonces el respaldo con IA.

**Las tres barreras van antes de abrir nada**, y en ese orden a propósito:
rechazar por tamaño es una comparación de enteros, rechazar por extensión es
una comparación de cadenas, y comprobar la firma son cuatro bytes. Abrir el
archivo es lo caro, así que es lo último. Un `.doc` renombrado a `.docx` lo
atrapa la firma, no la extensión.

El respaldo con IA corre **solo** cuando el archivo se abrió bien y la lectura
no reconoció nada (RF-05c). Un archivo que no se pudo abrir no llega al
respaldo: no tiene texto que mandar, y además su error es distinto para el
Administrador.
"""

import logging
from dataclasses import dataclass

from app.configuracion import obtener_configuracion
from app.formatos import lector_excel, lector_word, propuesta_ia, texto_para_ia

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
    """Dañado, protegido o no se pudo abrir → `422` con su mensaje (RF-10)."""


class SinEstructuraReconocible(ErrorDeFormato):
    """Ni la lectura ni la IA reconocieron nada → `422` con su mensaje (RF-10).

    Es el mismo error cuando el respaldo está apagado, cuando no respondió y
    cuando su propuesta quedó vacía: para el Administrador las tres son lo
    mismo, y nombrarle una falla de un servicio interno no le da nada con lo
    que actuar.
    """


@dataclass(frozen=True)
class FormatoReconocido:
    """Lo que la puerta devuelve cuando el archivo sirve."""

    extension: str
    estructura: dict


_LECTORES = {"docx": lector_word, "xlsx": lector_excel}


def extension_de(nombre_archivo: str) -> str:
    """La extensión del nombre, en minúsculas y sin punto."""
    _, _, extension = nombre_archivo.rpartition(".")
    return extension.lower()


def reconocer(contenido: bytes, nombre_archivo: str) -> FormatoReconocido:
    """Valida el archivo y devuelve su estructura, o levanta un `ErrorDeFormato`."""
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

    # --- Lectura directa, que tiene prioridad ---
    try:
        estructura = lector.leer(contenido)
    except lector.ErrorDeLectura as error:
        raise ArchivoIlegible(
            "No se pudo leer el archivo. Puede estar dañado o protegido con "
            "contraseña."
        ) from error

    if not lector.sin_estructura(estructura):
        return FormatoReconocido(extension=extension, estructura=estructura)

    # --- Respaldo con IA (RF-05c), solo si la lectura no reconoció nada ---
    registro.info(
        "La lectura directa no reconoció estructura en un %s; se intenta el respaldo.",
        extension,
    )
    esqueleto = texto_para_ia.extraer(contenido, extension)
    propuesta = propuesta_ia.proponer(esqueleto)

    if propuesta is None:
        raise SinEstructuraReconocible(
            "No se reconoció ninguna estructura en el archivo. Revisa que el "
            "formato tenga secciones con estilo de título, o encabezados de "
            "columna."
        )

    return FormatoReconocido(extension=extension, estructura=propuesta)


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
