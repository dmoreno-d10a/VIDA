"""Contraseñas: hash y política.

Dos responsabilidades, las dos con una regla dura detrás:

1. **El hash.** Argon2id, con sal propia por contraseña. La contraseña legible
   no se guarda ni se devuelve nunca, a nadie, tampoco al Administrador
   (RF-19).
2. **La política.** Longitud, lista de contraseñas comunes, no contener la
   identificación y no repetir la anterior. Todos los valores salen de
   configuración (RF-20, RF-23); aquí no hay números fijos.
"""

from functools import lru_cache
from pathlib import Path

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from app.configuracion import obtener_configuracion

_hasher = PasswordHasher()


class ErrorDePolitica(ValueError):
    """La contraseña propuesta no cumple la política vigente."""


def calcular_hash(contrasena: str) -> str:
    """Devuelve el hash Argon2id de la contraseña.

    Dos llamadas con la misma contraseña devuelven hashes distintos, porque
    cada uno lleva su propia sal.
    """
    return _hasher.hash(contrasena)


def verificar(contrasena: str, hash_guardado: str) -> bool:
    """Indica si la contraseña corresponde al hash guardado."""
    try:
        return _hasher.verify(hash_guardado, contrasena)
    except (VerifyMismatchError, InvalidHashError):
        return False


@lru_cache
def _contrasenas_comunes(ruta: Path, marca_de_tiempo: float) -> frozenset[str]:
    """Lee la lista de contraseñas comunes, en minúsculas.

    `marca_de_tiempo` entra en la clave de caché para que, si el archivo se
    reemplaza, la lista se vuelva a leer.
    """
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    return frozenset(
        linea.strip().lower()
        for linea in lineas
        if linea.strip() and not linea.strip().startswith("#")
    )


def contrasenas_comunes() -> frozenset[str]:
    """Lista de contraseñas rechazadas, según la ruta configurada."""
    ruta = obtener_configuracion().ruta_contrasenas_comunes
    try:
        marca = ruta.stat().st_mtime
    except OSError as error:
        raise ErrorDePolitica(
            f"No se pudo leer la lista de contraseñas comunes en {ruta}. "
            "Revisa VIDA_CONTRASENAS_COMUNES."
        ) from error
    return _contrasenas_comunes(ruta, marca)


def _parte_local(identificacion: str) -> str:
    """Parte de la identificación que no conviene dejar en la contraseña."""
    return identificacion.split("@", 1)[0].strip().lower()


def validar_politica(
    contrasena: str,
    *,
    identificacion: str,
    hash_anterior: str | None = None,
) -> None:
    """Valida la contraseña contra la política vigente.

    No devuelve nada: si algo no cumple, lanza `ErrorDePolitica` con el motivo
    en español, para poder decirle al usuario **qué** regla incumplió sin
    decirle nada sobre otras cuentas.
    """
    configuracion = obtener_configuracion()

    if len(contrasena) < configuracion.contrasena_min:
        raise ErrorDePolitica(
            f"La contraseña debe tener al menos {configuracion.contrasena_min} "
            "caracteres."
        )

    if len(contrasena) > configuracion.contrasena_max:
        raise ErrorDePolitica(
            f"La contraseña no puede pasar de {configuracion.contrasena_max} "
            "caracteres."
        )

    if contrasena.lower() in contrasenas_comunes():
        raise ErrorDePolitica(
            "Esa contraseña es de uso común y es de las primeras que se "
            "prueban. Elige otra."
        )

    parte_local = _parte_local(identificacion)
    if parte_local and parte_local in contrasena.lower():
        raise ErrorDePolitica(
            "La contraseña no puede contener tu identificación de usuario."
        )

    if hash_anterior and verificar(contrasena, hash_anterior):
        raise ErrorDePolitica(
            "La contraseña nueva no puede ser la misma que ya tenías."
        )


def calcular_hash_validado(
    contrasena: str,
    *,
    identificacion: str,
    hash_anterior: str | None = None,
) -> str:
    """Valida la política y devuelve el hash. Es la puerta única de entrada.

    Las tres situaciones donde se fija una contraseña —crear el usuario,
    cambiarla el propio usuario y restablecerla el Administrador— pasan por
    aquí, para que ninguna se salte la política.
    """
    validar_politica(
        contrasena, identificacion=identificacion, hash_anterior=hash_anterior
    )
    return calcular_hash(contrasena)
