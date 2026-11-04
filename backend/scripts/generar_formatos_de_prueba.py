"""Genera los cuatro formatos de prueba de la funcionalidad 002.

    python -m scripts.generar_formatos_de_prueba

Los cuatro son **ficticios** y se generan al correr el script: en el
repositorio no queda ningún binario, y el formato real del cliente (el Adapter
Reverso de verdad) no entra nunca aquí (Art. X.3). Lo que se replica es la
*forma* del documento, con contenido inventado para la ocasión.

Cada formato trae al lado su **estructura esperada**, como dato y no como
código. Esa es la parte que hace que el Art. II sea verificable: una prueba
compara lo que el reconocimiento produjo contra este diccionario, en vez de
contra lo que le parezca a quien la escribe.

Los cuatro casos:

- `referencia-adapter-reverso.docx` — el formato que el área usa hoy, con
  estilos de título bien puestos. Es el caso de referencia.
- `generalizacion-word.docx` — otra jerarquía, dos títulos con el mismo nombre
  y uno sin texto. Es el «caso distinto al de referencia» que exige el
  Art. VIII, más los casos borde de la sección 7 de la spec.
- `generalizacion-excel.xlsx` — tres hojas, una con los encabezados en la fila
  3 y dos columnas con el mismo nombre.
- `solo-negritas.docx` — secciones marcadas con negrita y sin un solo estilo de
  título. Para la lectura determinista es un archivo sin estructura, y es el
  único caso que ejercita el respaldo con IA (RF-05c): sin él no hay forma de
  probarlo.
"""

import tempfile
from pathlib import Path

from docx import Document
from docx.shared import Pt
from openpyxl import Workbook

# ---------------------------------------------------------------- referencia

# `nivel` es el del estilo de título: «Heading 1» es 1. La lista está en el
# orden del archivo, y ese orden es el dato (Art. I).
#
# El documento de referencia lleva además un título con el estilo `Title`, que
# esta estructura **no** incluye: es el título del documento, no una de sus
# secciones. Queda escrito aquí porque es una decisión y no un descuido, y el
# lector de Word (T016) tiene que tomar la misma: cuenta `Heading N`, no
# `Title`.
REFERENCIA_SECCIONES = [
    ("Contexto del servicio", 1),
    ("Objetivo", 2),
    ("Alcance", 2),
    ("Definición del servicio", 1),
    ("Request", 2),
    ("Response", 2),
    ("Códigos de error", 2),
    ("Reglas de negocio", 1),
    ("Consideraciones técnicas", 1),
]

ESTRUCTURA_REFERENCIA = {
    "clase": "word",
    "secciones": [{"nombre": n, "nivel": v} for n, v in REFERENCIA_SECCIONES],
}

# ------------------------------------------------------------ generalización

# Empieza en nivel 2 y no en 1 (una jerarquía que no es la de referencia),
# «Detalle» aparece dos veces, y hay un título sin texto.
GENERALIZACION_SECCIONES = [
    ("Resumen ejecutivo", 2),
    ("Detalle", 3),
    ("Anexo", 1),
    ("Detalle", 3),
    (None, 2),
    ("Cierre", 4),
]

ESTRUCTURA_GENERALIZACION = {
    "clase": "word",
    "secciones": [{"nombre": n, "nivel": v} for n, v in GENERALIZACION_SECCIONES],
}

# -------------------------------------------------------------------- Excel

# `fila` es dónde empiezan los encabezados. «Response» los trae en la 3 porque
# arriba hay un título y una fila en blanco, que es lo que hace la mayoría de
# los formatos de verdad. «Notas» no tiene encabezados: es válida, y es lo que
# obliga a que «sin estructura» signifique *ninguna* hoja con columnas.
EXCEL_HOJAS = [
    ("Request", 1, ["Campo", "Tipo", "Obligatorio", "Campo"]),
    ("Response", 3, ["Campo", "Tipo", "Descripción"]),
    ("Notas", None, []),
]

ESTRUCTURA_EXCEL = {
    "clase": "excel",
    "hojas": [
        {
            "nombre": nombre,
            "fila_de_encabezados": fila,
            "columnas": list(columnas),
        }
        for nombre, fila, columnas in EXCEL_HOJAS
    ],
}

# --------------------------------------------------------------- negritas

SOLO_NEGRITAS_SECCIONES = [
    "Contexto",
    "Entradas",
    "Salidas",
    "Validaciones",
]

# La lectura determinista no reconoce nada aquí, y eso es el punto del caso.
ESTRUCTURA_SOLO_NEGRITAS_LEIDA = {"clase": "word", "secciones": []}

# Lo que una propuesta de la IA tendría que nombrar. No es «la respuesta
# correcta» del modelo —no se le exige una lista idéntica—, sino el conjunto
# del que todo nombre propuesto debe salir: cada uno aparece literalmente en el
# documento, que es lo que RF-05d verifica.
NOMBRES_LITERALES_SOLO_NEGRITAS = list(SOLO_NEGRITAS_SECCIONES)


def _parrafo_de_relleno(documento: Document, texto: str) -> None:
    """Texto ficticio bajo una sección, para que el archivo no esté vacío."""
    documento.add_paragraph(texto)


def generar_referencia(destino: Path) -> Path:
    """El formato de referencia, con estilos de título."""
    documento = Document()
    documento.add_heading("Documento de servicio", 0)
    for nombre, nivel in REFERENCIA_SECCIONES:
        documento.add_heading(nombre, nivel)
        _parrafo_de_relleno(
            documento, f"Contenido ficticio de «{nombre}». No es de ningún cliente."
        )
    ruta = destino / "referencia-adapter-reverso.docx"
    documento.save(ruta)
    return ruta


def generar_generalizacion_word(destino: Path) -> Path:
    """Otra jerarquía, nombres repetidos y un título sin texto."""
    documento = Document()
    for nombre, nivel in GENERALIZACION_SECCIONES:
        # `add_heading(None)` no sirve: hay que crear el título vacío.
        documento.add_heading(nombre if nombre is not None else "", nivel)
        _parrafo_de_relleno(documento, "Contenido ficticio de generalización.")
    ruta = destino / "generalizacion-word.docx"
    documento.save(ruta)
    return ruta


def generar_generalizacion_excel(destino: Path) -> Path:
    """Tres hojas, una con encabezados en la fila 3 y columnas repetidas."""
    libro = Workbook()
    libro.remove(libro.active)

    for nombre, fila, columnas in EXCEL_HOJAS:
        hoja = libro.create_sheet(nombre)
        if fila is None:
            continue
        # Lo que va arriba de los encabezados cuando no empiezan en la fila 1:
        # un título y una fila en blanco, como en los formatos de verdad.
        if fila > 1:
            hoja.cell(row=1, column=1, value=f"Hoja de {nombre} — formato ficticio")
        for columna, encabezado in enumerate(columnas, start=1):
            hoja.cell(row=fila, column=columna, value=encabezado)
        # Una fila de datos ficticios, para que la hoja no sea solo encabezados.
        for columna, _ in enumerate(columnas, start=1):
            hoja.cell(row=fila + 1, column=columna, value="(ficticio)")

    ruta = destino / "generalizacion-excel.xlsx"
    libro.save(ruta)
    return ruta


def generar_solo_negritas(destino: Path) -> Path:
    """Secciones en negrita, sin un solo estilo de título.

    Para una persona es un documento con cuatro secciones; para `python-docx`
    es un archivo sin estructura. Esa diferencia es el caso.
    """
    documento = Document()
    for nombre in SOLO_NEGRITAS_SECCIONES:
        parrafo = documento.add_paragraph()
        trozo = parrafo.add_run(nombre)
        trozo.bold = True
        trozo.font.size = Pt(14)
        _parrafo_de_relleno(documento, f"Contenido ficticio bajo «{nombre}».")
    ruta = destino / "solo-negritas.docx"
    documento.save(ruta)
    return ruta


def generar_todos(destino: Path) -> dict[str, Path]:
    """Genera los cuatro formatos en `destino` y devuelve dónde quedó cada uno."""
    destino.mkdir(parents=True, exist_ok=True)
    return {
        "referencia": generar_referencia(destino),
        "generalizacion_word": generar_generalizacion_word(destino),
        "generalizacion_excel": generar_generalizacion_excel(destino),
        "solo_negritas": generar_solo_negritas(destino),
    }


def main() -> None:
    """Genera los cuatro formatos en una carpeta temporal y dice dónde."""
    destino = Path(tempfile.mkdtemp(prefix="vida-formatos-"))
    archivos = generar_todos(destino)
    print(f"Formatos de prueba generados en {destino}\n")
    for clave, ruta in archivos.items():
        print(f"  {clave:22} {ruta.name:36} {ruta.stat().st_size:>8} bytes")
    print(
        "\nTodos son ficticios. Ninguno queda versionado en el repositorio "
        "(Art. X.3)."
    )


if __name__ == "__main__":
    main()
