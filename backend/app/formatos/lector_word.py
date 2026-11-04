"""Lectura de la estructura de un formato de Word.

Una sección es un párrafo con **estilo de título** (RF-05a). Se reconoce por
la marca que Word guarda dentro del archivo (`Heading1`, `Heading2`, …), que
es la misma en cualquier idioma: el nombre que se ve en pantalla cambia con el
idioma de Office, y leer por ahí haría que el mismo archivo se reconociera
distinto según quién lo abrió.

El estilo `Title` **no** cuenta: es el título del documento, no una de sus
secciones.

Lo que este lector **no** hace, por el Art. I: no agrega secciones que no
estén, no renombra, no reordena, no fusiona las de nombre repetido y no le
inventa un nombre a un título vacío.
"""

import re
from io import BytesIO

from docx import Document
from docx.opc.exceptions import PackageNotFoundError

# `Heading1`…`Heading9` es el identificador interno del estilo. `HeadingN` sin
# número no existe; `Title` existe y queda fuera a propósito.
_ESTILO_DE_TITULO = re.compile(r"^Heading(\d)$")


class ErrorDeLectura(Exception):
    """El archivo no se pudo abrir: dañado, protegido o no es un `.docx`.

    Es distinto de «se abrió pero no tiene estructura»: el contrato les da
    mensajes distintos, porque el Administrador puede corregir lo segundo y no
    lo primero.
    """


def _nivel_de(parrafo) -> int | None:
    """El nivel del párrafo si es un título, o `None` si no lo es."""
    identificador = parrafo.style.style_id or ""
    coincidencia = _ESTILO_DE_TITULO.match(identificador)
    return int(coincidencia.group(1)) if coincidencia else None


def leer(contenido: bytes) -> dict:
    """Devuelve la estructura de un `.docx`, en el orden del documento."""
    try:
        documento = Document(BytesIO(contenido))
    except PackageNotFoundError as error:
        raise ErrorDeLectura(
            "El archivo no se pudo abrir como documento de Word."
        ) from error
    except Exception as error:  # noqa: BLE001
        # `python-docx` levanta errores de varias clases cuando el paquete está
        # corrupto o cifrado. Todos significan lo mismo para quien llama, y
        # dejarlos escapar convertiría un archivo malo en un error 500.
        raise ErrorDeLectura(
            "El archivo no se pudo leer. Puede estar dañado o protegido."
        ) from error

    secciones = []
    for parrafo in documento.paragraphs:
        nivel = _nivel_de(parrafo)
        if nivel is None:
            continue
        texto = parrafo.text.strip()
        # Un título sin texto se registra como viene, con `nombre` nulo
        # (RF-11). La posición en la lista lo identifica.
        secciones.append({"nombre": texto or None, "nivel": nivel})

    return {"clase": "word", "secciones": secciones}


def sin_estructura(estructura: dict) -> bool:
    """Si de este Word no se reconoció ninguna sección.

    No es el rechazo: es la condición que dispara el respaldo con IA (RF-05c).
    """
    return not estructura.get("secciones")
