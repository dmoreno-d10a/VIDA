"""Almacén de los archivos de formato que carga el Administrador.

Guarda el archivo en disco y devuelve una ruta **relativa** al almacén
configurado, que es lo que se escribe en la base de datos (RF-09, RF-20). La
ruta es relativa a propósito: una ruta absoluta guardada en la base rompe el
sistema en cuanto se mueve el almacén, se despliega en otra máquina o se
trabaja en un worktree con otra configuración.

El nombre con el que se guarda sale del **SHA-256 del contenido**, no del
nombre que trajo el usuario. Ese nombre puede traer acentos, barras o
caracteres que el sistema de archivos no acepte, y dos administradores pueden
cargar dos archivos distintos llamados igual. El nombre original se conserva,
pero en la base de datos (`nombre_archivo_original`), que es donde no estorba.
"""

import hashlib
from dataclasses import dataclass
from pathlib import Path

from app.configuracion import obtener_configuracion


class ErrorDeAlmacen(Exception):
    """El archivo no se pudo guardar o leer.

    Existe para que quien llama distinga «el almacén falló» de cualquier otro
    `OSError` del proceso, y pueda responderle al Administrador que el problema
    no es su archivo.
    """


@dataclass(frozen=True)
class FormatoGuardado:
    """Lo que el almacén devuelve tras guardar un archivo."""

    ruta_relativa: str
    """Relativa al almacén configurado. Es lo que va a la base de datos."""

    hash_sha256: str
    """Del contenido. Es también el nombre con el que se guardó."""

    tamano_bytes: int


def _raiz() -> Path:
    """La carpeta del almacén, según la configuración vigente.

    Se consulta en cada llamada y no al importar: las pruebas apuntan el
    almacén a una carpeta temporal, y un valor capturado al importar dejaría
    ese cambio sin efecto.
    """
    return obtener_configuracion().ruta_almacen_formatos


def guardar(contenido: bytes, extension: str) -> FormatoGuardado:
    """Guarda el contenido en el almacén y devuelve dónde quedó.

    Si el mismo archivo se carga dos veces, el contenido se escribe una sola
    vez: el nombre es el hash, así que la segunda escritura es idéntica. Eso
    **no** significa que no se cree una versión nueva — la versión la decide
    quien llama, y el historial es asunto de la base de datos (RF-21).
    """
    sha256 = hashlib.sha256(contenido).hexdigest()
    extension = extension.lstrip(".").lower()

    # Dos niveles de subcarpeta por los dos primeros pares del hash. Con miles
    # de formatos, una sola carpeta se vuelve lenta de listar en algunos
    # sistemas de archivos, y esto se reparte solo.
    relativa = Path(sha256[:2]) / sha256[2:4] / f"{sha256}.{extension}"
    destino = _raiz() / relativa

    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        # `wb` y no `xb`: si el archivo ya está, se reescribe con el mismo
        # contenido, porque el nombre es el hash de ese contenido.
        destino.write_bytes(contenido)
    except OSError as error:
        raise ErrorDeAlmacen(
            f"No se pudo guardar el formato en el almacén: {error}"
        ) from error

    # Siempre con `/`, también en Windows: la ruta se guarda en la base de
    # datos y la puede leer una instalación con otro separador.
    return FormatoGuardado(
        ruta_relativa=relativa.as_posix(),
        hash_sha256=sha256,
        tamano_bytes=len(contenido),
    )


def leer(ruta_relativa: str) -> bytes:
    """Lee un archivo del almacén a partir de la ruta que guardó `guardar`."""
    destino = ruta_para(ruta_relativa)
    try:
        return destino.read_bytes()
    except OSError as error:
        raise ErrorDeAlmacen(
            f"No se pudo leer el formato {ruta_relativa!r} del almacén: {error}"
        ) from error


def ruta_para(ruta_relativa: str) -> Path:
    """La ruta absoluta de un archivo del almacén.

    Rechaza cualquier ruta que salga del almacén. Las rutas las escribe esta
    misma plataforma, pero una ruta de la base de datos es un dato, y un dato
    que sirve para abrir archivos se valida antes de usarse.
    """
    raiz = _raiz().resolve()
    destino = (raiz / ruta_relativa).resolve()
    if not destino.is_relative_to(raiz):
        raise ErrorDeAlmacen(
            f"La ruta {ruta_relativa!r} apunta fuera del almacén de formatos."
        )
    return destino
