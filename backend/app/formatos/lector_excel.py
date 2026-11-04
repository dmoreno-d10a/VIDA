"""Lectura de la estructura de un formato de Excel.

Las columnas salen de la **primera fila con dos o más celdas con contenido**,
y la estructura registra cuál fue (`fila_de_encabezados`), para que la
decisión quede a la vista del Administrador y no escondida (RF-05b). Fijar la
fila 1 rechazaría formatos legítimos: muchos traen arriba un título o un logo.

**Por qué dos celdas y no una.** «La primera fila con contenido», al pie de la
letra, toma el título que el formato trae arriba —que es *una* celda— en vez
de los encabezados que vienen más abajo, y entonces la regla no hace lo que su
propia razón dice que debe hacer. Un título ocupa una celda; una fila de
encabezados tiene varias. Si ninguna fila llega a dos, se toma la primera con
algo: un formato de una sola columna es raro pero legítimo, y rechazarlo sería
peor que reconocerle su única columna.

Se lee en modo **solo lectura**: un `.xlsx` de 25 MB abierto por completo
carga todas las celdas en memoria, y de un formato solo hacen falta las
primeras filas.

Lo que este lector **no** hace, por el Art. I: no fusiona dos columnas que se
llamen igual, no las renumera, no reordena las hojas y no le inventa un nombre
a una columna sin encabezado.
"""

from io import BytesIO

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

# Cuántas filas se miran buscando la primera con contenido. Si en las primeras
# veinte no hay nada, la hoja se da por sin encabezados: seguir bajando por una
# hoja de miles de filas vacías cuesta y no encuentra formatos reales.
FILAS_QUE_SE_MIRAN = 20


class ErrorDeLectura(Exception):
    """El archivo no se pudo abrir: dañado, protegido o no es un `.xlsx`."""


def _fila_de_encabezados(hoja) -> tuple[int | None, list[str]]:
    """La fila de encabezados de la hoja, y cuáles son.

    La primera con dos o más celdas con contenido; si ninguna llega a dos, la
    primera con una. Devuelve `(None, [])` si no hay ninguna con nada: es una
    hoja sin encabezados, que es válida.
    """
    primera_con_una: tuple[int, list[str]] | None = None

    for numero, fila in enumerate(
        hoja.iter_rows(max_row=FILAS_QUE_SE_MIRAN, values_only=True), start=1
    ):
        valores = [
            str(celda).strip()
            for celda in fila
            if celda is not None and str(celda).strip() != ""
        ]
        if len(valores) >= 2:
            return numero, valores
        if valores and primera_con_una is None:
            primera_con_una = (numero, valores)

    return primera_con_una if primera_con_una is not None else (None, [])


def leer(contenido: bytes) -> dict:
    """Devuelve la estructura de un `.xlsx`, con las hojas en orden del libro."""
    try:
        libro = load_workbook(BytesIO(contenido), read_only=True, data_only=True)
    except InvalidFileException as error:
        raise ErrorDeLectura(
            "El archivo no se pudo abrir como libro de Excel."
        ) from error
    except Exception as error:  # noqa: BLE001
        # Igual que en Word: un paquete corrupto o cifrado levanta errores de
        # varias clases, y todos significan lo mismo para quien llama.
        raise ErrorDeLectura(
            "El archivo no se pudo leer. Puede estar dañado o protegido."
        ) from error

    hojas = []
    try:
        for nombre in libro.sheetnames:
            fila, columnas = _fila_de_encabezados(libro[nombre])
            hojas.append(
                {
                    "nombre": nombre,
                    "fila_de_encabezados": fila,
                    "columnas": columnas,
                }
            )
    finally:
        # En modo solo lectura hay que cerrar a mano: si no, el archivo
        # temporal que openpyxl abrió queda tomado.
        libro.close()

    return {"clase": "excel", "hojas": hojas}


def sin_estructura(estructura: dict) -> bool:
    """Si de este Excel no se reconoció nada.

    Un libro con hojas pero sin un solo encabezado no sirve para generar nada,
    así que cuenta como sin estructura. Una hoja suelta sin encabezados, en
    cambio, es válida mientras alguna otra tenga columnas.
    """
    return not any(hoja["columnas"] for hoja in estructura.get("hojas", []))
