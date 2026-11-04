"""El esqueleto del documento que se le manda a la IA cuando hace falta.

**Nunca el archivo.** El Art. VI lo prohíbe, y además no haría falta: para
proponer qué secciones tiene un documento basta el texto de sus párrafos con
las señales de forma que una persona usaría para reconocerlos —negrita,
tamaño de letra, qué tan corto es el párrafo—. El contenido de cada sección no
se manda: no aporta a la pregunta y es lo que más pesa.

Este módulo también produce la **lista de los textos literales** del
documento. Es la misma lista contra la que `propuesta_ia` descarta lo que el
modelo haya inventado (RF-05d), y vive aquí para que no puedan separarse: si
el descarte comparara contra un texto distinto del que se mandó, podría tirar
un nombre que sí estaba en el documento.
"""

from dataclasses import dataclass, field
from io import BytesIO

from docx import Document
from openpyxl import load_workbook

# Cuántos párrafos u hojas se mandan como máximo. Un formato tiene decenas de
# párrafos, no miles; el techo está para que un archivo anómalo no convierta
# una consulta en un gasto abierto (Art. VI).
MAXIMO_PARRAFOS = 400
MAXIMO_FILAS_POR_HOJA = 5

# Un párrafo más largo que esto es contenido, no un encabezado. Se manda
# recortado: lo que importa es que la IA vea que ahí hay texto corrido, no qué
# dice.
LARGO_MAXIMO_DE_PARRAFO = 200


@dataclass
class EsqueletoDelDocumento:
    """Lo que se le manda a la IA, y los textos literales para el descarte."""

    descripcion: str
    """El esqueleto, ya en texto, listo para ir en la consulta."""

    textos_literales: list[str] = field(default_factory=list)
    """Cada texto tal como aparece en el documento.

    `propuesta_ia` descarta todo nombre propuesto que no esté aquí (RF-05d).
    """


def _senales(parrafo) -> str:
    """Las señales de forma del párrafo, como las vería una persona."""
    marcas = []
    trozos = [t for t in parrafo.runs if t.text.strip()]
    if trozos and all(t.bold for t in trozos):
        marcas.append("negrita")
    if trozos and all(t.underline for t in trozos):
        marcas.append("subrayado")
    tamanos = {t.font.size.pt for t in trozos if t.font.size is not None}
    if tamanos:
        marcas.append(f"{max(tamanos):.0f}pt")
    if len(parrafo.text.strip()) <= 60:
        marcas.append("corto")
    return ", ".join(marcas) if marcas else "sin señales"


def de_word(contenido: bytes) -> EsqueletoDelDocumento:
    """El esqueleto de un `.docx`: párrafos en orden con sus señales."""
    documento = Document(BytesIO(contenido))

    lineas = []
    literales = []
    for parrafo in documento.paragraphs[:MAXIMO_PARRAFOS]:
        texto = parrafo.text.strip()
        if not texto:
            continue
        literales.append(texto)
        recortado = texto[:LARGO_MAXIMO_DE_PARRAFO]
        lineas.append(f"[{_senales(parrafo)}] {recortado}")

    return EsqueletoDelDocumento(
        descripcion="\n".join(lineas), textos_literales=literales
    )


def de_excel(contenido: bytes) -> EsqueletoDelDocumento:
    """El esqueleto de un `.xlsx`: hojas con sus primeras filas."""
    libro = load_workbook(BytesIO(contenido), read_only=True, data_only=True)

    lineas = []
    literales = []
    try:
        for nombre in libro.sheetnames:
            literales.append(nombre)
            lineas.append(f"Hoja: {nombre}")
            hoja = libro[nombre]
            for numero, fila in enumerate(
                hoja.iter_rows(max_row=MAXIMO_FILAS_POR_HOJA, values_only=True),
                start=1,
            ):
                celdas = [
                    str(celda).strip()
                    for celda in fila
                    if celda is not None and str(celda).strip() != ""
                ]
                if not celdas:
                    continue
                literales.extend(celdas)
                lineas.append(f"  fila {numero}: " + " | ".join(celdas))
    finally:
        libro.close()

    return EsqueletoDelDocumento(
        descripcion="\n".join(lineas), textos_literales=literales
    )


def extraer(contenido: bytes, extension: str) -> EsqueletoDelDocumento:
    """El esqueleto del archivo, según su extensión."""
    if extension == "docx":
        return de_word(contenido)
    if extension == "xlsx":
        return de_excel(contenido)
    raise ValueError(f"No hay esqueleto definido para la extensión {extension!r}.")
