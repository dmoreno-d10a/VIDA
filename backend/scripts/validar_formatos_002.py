"""Validación de la funcionalidad 002 (tareas T033 a T038a).

    python -m scripts.validar_formatos_002

Ejecuta las comprobaciones de la fase 9 y escribe su resultado, para que lo
que vaya en el Pull Request sea una medición y no una afirmación. No toca la
base de datos: trabaja contra el reconocimiento directamente, que es donde
viven las reglas que se están validando.

Lo que **no** puede hacer este guion es la segunda mitad de T035: medir la
carga con el respaldo con IA contra VORKAN de verdad. Hace falta una
credencial, y una credencial no entra al repositorio (Art. X.2). Esa medición
la hace quien tenga el entorno, y el guion lo dice en su salida en vez de
dejar el hueco callado.
"""

import sys
import time
from pathlib import Path
from tempfile import mkdtemp

from openpyxl import Workbook

from app.configuracion import obtener_configuracion
from app.formatos import propuesta_ia, reconocimiento
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

    # El respaldo se sustituye por un contador: este guion no sale a la red, y
    # lo que mide es cuántas veces *habría* salido.
    llamadas: list[str] = []
    propuesta_ia.consultar_litellm = lambda mensaje: (  # type: ignore[assignment]
        llamadas.append(mensaje) or "{}"
    )

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

    print("\nT038a — La lectura directa tiene prioridad (Art. VI)")
    comprobar(
        "los tres formatos bien marcados no costaron ni una llamada a LiteLLM",
        len(llamadas) == 0,
        f"{len(llamadas)} llamadas",
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
        "    OJO: esto mide el análisis en el servidor, no punta a punta. Lo que\n"
        "    falta —la subida por la red y el caso con el respaldo con IA contra\n"
        "    VORKAN— se mide con el entorno completo: ver el encabezado de este\n"
        "    guion."
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

    print("\nT038 — El límite y el modelo son configuración (RF-18, CE-08, Art. V)")
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
    comprobar(
        "la tarea del modelo sale de la configuración y no del código",
        bool(configuracion.modelo_reconocimiento),
        configuracion.modelo_reconocimiento,
    )
    comprobar(
        "sin credencial el respaldo queda indisponible y la plataforma arranca",
        configuracion.respaldo_ia_disponible == bool(configuracion.litellm_api_key),
        "disponible" if configuracion.respaldo_ia_disponible else "indisponible",
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
