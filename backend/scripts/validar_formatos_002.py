"""Validación de la funcionalidad 002 (tareas T033 a T038).

    python -m scripts.validar_formatos_002

Ejecuta las comprobaciones de la fase 9 y escribe su resultado, para que lo
que vaya en el Pull Request sea una medición y no una afirmación. No toca la
base de datos: trabaja contra el reconocimiento directamente, que es donde
viven las reglas que se están validando.

Lo que mide es el análisis en el servidor. La medición punta a punta que pide
CE-09 —con la subida del archivo por la red incluida— necesita el entorno
completo, y la hace quien lo tenga.
"""

import sys
import time
from pathlib import Path
from tempfile import mkdtemp

from openpyxl import Workbook

from app.configuracion import obtener_configuracion
from app.formatos import reconocimiento
from scripts.generar_formatos_de_prueba import (
    ESTRUCTURA_EXCEL,
    ESTRUCTURA_GENERALIZACION,
    ESTRUCTURA_REFERENCIA,
    generar_todos,
)

TECHO_SEGUNDOS = 30.0

resultados: list[tuple[str, bool, str]] = []


def comprobar(etiqueta: str, condicion: bool, detalle: str = "") -> None:
    resultados.append((etiqueta, condicion, detalle))
    marca = "OK  " if condicion else "FALLA"
    print(f"  [{marca}] {etiqueta}" + (f" — {detalle}" if detalle else ""))


def _escribir_libro(ruta: Path, hojas: int) -> int:
    """Escribe un `.xlsx` con esa cantidad de hojas y devuelve su tamaño.

    `write_only` es lo que permite construirlo sin tener el libro entero en
    memoria. Los valores van variados a propósito: un `.xlsx` es un ZIP, y con
    celdas repetidas comprime tanto que harían falta cientos de miles de filas
    para llegar a 25 MB en disco.
    """
    libro = Workbook(write_only=True)
    for numero in range(hojas):
        hoja = libro.create_sheet(f"Hoja {numero + 1}")
        hoja.append([f"Columna {c}" for c in range(1, 26)])
        for fila in range(3000):
            hoja.append(
                [
                    f"v{numero}-{fila}-{c}-{(fila * c * 7919) % 99991}"
                    for c in range(1, 26)
                ]
            )
    libro.save(ruta)
    return ruta.stat().st_size


def excel_cerca_del_limite(destino: Path) -> Path:
    """Un `.xlsx` justo por debajo del límite, con muchas hojas (T035).

    Se genera y no se versiona: 25 MB de binario no entran al repositorio.

    El tamaño se **calibra**: cuánto pesa un `.xlsx` depende de cuánto
    comprima su contenido, así que se escribe una vez, se mide y se ajusta la
    cantidad de hojas. Apuntar a ojo da un archivo de 4 MB o de 69, y ninguno
    de los dos mide lo que CE-09 pide medir.
    """
    objetivo = obtener_configuracion().formato_tamano_max_bytes
    ruta = destino / "grande.xlsx"

    hojas = 40
    for intento in range(4):
        tamano = _escribir_libro(ruta, hojas)
        print(
            f"    intento {intento + 1}: {hojas} hojas dan "
            f"{tamano / 1024 / 1024:.1f} MB"
        )
        # Entre el 85 % y el 100 % del límite: cerca del peor caso admitido,
        # sin pasarse y volverse un archivo que la plataforma rechaza.
        if 0.85 * objetivo <= tamano < objetivo:
            break
        siguiente = max(1, round(hojas * (0.95 * objetivo) / tamano))
        if siguiente == hojas:
            break
        hojas = siguiente

    print(
        f"    archivo de la medición: {ruta.stat().st_size / 1024 / 1024:.1f} MB "
        f"(límite configurado: {objetivo / 1024 / 1024:.0f} MB)"
    )
    return ruta


def main() -> int:
    carpeta = Path(mkdtemp(prefix="vida-validacion-"))
    formatos = generar_todos(carpeta)
    configuracion = obtener_configuracion()

    print("\nT033 — Caso de referencia (CE-01)")
    reconocido = reconocimiento.reconocer(
        formatos["referencia"].read_bytes(), formatos["referencia"].name
    )
    comprobar(
        "la estructura del Word de referencia es exactamente la esperada",
        reconocido.estructura == ESTRUCTURA_REFERENCIA,
        f"{len(reconocido.estructura['secciones'])} secciones",
    )

    print("\nT034 — Casos de generalización (RF-17, CE-02, Art. VIII)")
    word = reconocimiento.reconocer(
        formatos["generalizacion_word"].read_bytes(),
        formatos["generalizacion_word"].name,
    )
    comprobar(
        "el Word ajeno al caso de referencia se reconoce exacto",
        word.estructura == ESTRUCTURA_GENERALIZACION,
    )
    comprobar(
        "el título sin texto queda como nulo, sin nombre inventado (RF-11)",
        sum(1 for s in word.estructura["secciones"] if s["nombre"] is None) == 1,
    )
    comprobar(
        "los dos títulos de nombre repetido se conservan los dos (RF-06)",
        sum(1 for s in word.estructura["secciones"] if s["nombre"] == "Detalle") == 2,
    )
    excel = reconocimiento.reconocer(
        formatos["generalizacion_excel"].read_bytes(),
        formatos["generalizacion_excel"].name,
    )
    comprobar(
        "el Excel ajeno al caso de referencia se reconoce exacto",
        excel.estructura == ESTRUCTURA_EXCEL,
    )
    comprobar(
        "los encabezados bajo un título salen de la fila 3 (RF-05b)",
        next(h for h in excel.estructura["hojas"] if h["nombre"] == "Response")[
            "fila_de_encabezados"
        ]
        == 3,
    )

    print("\nRF-10 — Un formato sin estructura reconocible se acepta igual")
    negritas = reconocimiento.reconocer(
        formatos["solo_negritas"].read_bytes(), formatos["solo_negritas"].name
    )
    comprobar(
        "el Word que marca sus secciones con negrita no se rechaza",
        negritas.estructura == {"clase": "word", "secciones": []},
        "aceptado, con la estructura vacía",
    )

    print("\nT035 — Carga de un archivo grande contra el techo de 30 s (CE-09)")
    grande = excel_cerca_del_limite(carpeta)
    contenido = grande.read_bytes()
    comienzo = time.monotonic()
    grande_reconocido = reconocimiento.reconocer(contenido, grande.name)
    transcurrido = time.monotonic() - comienzo
    comprobar(
        "el análisis del archivo grande cabe en el techo",
        transcurrido < TECHO_SEGUNDOS,
        f"{transcurrido:.2f} s de análisis, con "
        f"{len(grande_reconocido.estructura['hojas'])} hojas",
    )
    print(
        "    OJO: esto mide el análisis en el servidor. Lo que falta para CE-09\n"
        "    —la subida del archivo por la red— se mide con el entorno completo."
    )

    print("\nT036 — Cero datos inventados y todo rastreable (Art. II, Art. IX)")
    for clave in ("referencia", "generalizacion_word"):
        from docx import Document

        documento = Document(formatos[clave])
        textos = {p.text.strip() for p in documento.paragraphs}
        estructura = reconocimiento.reconocer(
            formatos[clave].read_bytes(), formatos[clave].name
        ).estructura
        inventados = [
            s["nombre"]
            for s in estructura["secciones"]
            if s["nombre"] is not None and s["nombre"] not in textos
        ]
        comprobar(
            f"ninguna sección de {clave} tiene un nombre que el archivo no traía",
            not inventados,
            f"{len(inventados)} inventados" if inventados else "",
        )

    print("\nT038 — El límite y las extensiones son configuración (RF-18, CE-08)")
    comprobar(
        "el techo de tamaño sale de la configuración",
        configuracion.formato_tamano_max_bytes
        == configuracion.formato_mb_max * 1024 * 1024,
        f"{configuracion.formato_mb_max} MB",
    )
    comprobar(
        "las extensiones admitidas salen de la configuración",
        configuracion.extensiones_admitidas == ("docx", "xlsx"),
        str(configuracion.extensiones_admitidas),
    )

    fallas = [etiqueta for etiqueta, ok, _ in resultados if not ok]
    print(f"\n{len(resultados) - len(fallas)} de {len(resultados)} comprobaciones OK")
    if fallas:
        print("\nFALLARON:")
        for etiqueta in fallas:
            print(f"  - {etiqueta}")
        return 1
    print(f"\nFormatos de la validación: {carpeta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
