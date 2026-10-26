"""Crea el Administrador inicial de V.I.D.A. (RF-18).

Se ejecuta una vez, en la puesta en marcha, porque solo un Administrador puede
crear usuarios y al instalar la plataforma no hay ninguno.

    python -m scripts.crear_admin

La identificación sale de `VIDA_ADMIN_INICIAL`. La contraseña sale de
`VIDA_ADMIN_INICIAL_CONTRASENA` o, si no está, se pide por consola **sin
mostrarla**. En ningún caso se escribe en el código ni en el repositorio
(Art. X.2), ni se imprime al terminar.
"""

import sys
from getpass import getpass

from sqlalchemy import func, select

from app.bd import FabricaDeSesiones
from app.configuracion import obtener_configuracion
from app.modelos.usuario import Rol, Usuario
from app.seguridad.contrasena import ErrorDePolitica, calcular_hash_validado


def _pedir_contrasena(identificacion: str) -> str:
    """Pide la contraseña por consola, dos veces, sin mostrarla."""
    primera = getpass(f"Contraseña para {identificacion}: ")
    segunda = getpass("Repítela: ")
    if primera != segunda:
        raise SystemExit("Las contraseñas no coinciden. No se creó nada.")
    return primera


def crear_administrador_inicial() -> int:
    """Crea el Administrador inicial. Devuelve el código de salida."""
    configuracion = obtener_configuracion()

    identificacion = (configuracion.admin_inicial or "").strip()
    if not identificacion:
        print(
            "Falta VIDA_ADMIN_INICIAL: define la identificación del "
            "Administrador inicial antes de ejecutar este comando.",
            file=sys.stderr,
        )
        return 1

    with FabricaDeSesiones() as sesion_bd:
        # Si ya hay un Administrador activo, no se hace nada: ejecutar esto
        # dos veces no debe crear un duplicado ni cambiar nada.
        ya_hay = sesion_bd.scalar(
            select(func.count())
            .select_from(Usuario)
            .where(Usuario.rol == Rol.ADMINISTRADOR, Usuario.activo.is_(True))
        )
        if ya_hay:
            print(
                "Ya existe un Administrador activo. No se creó ninguno nuevo; "
                "los demás usuarios se crean desde la plataforma."
            )
            return 0

        contrasena = configuracion.admin_inicial_contrasena or _pedir_contrasena(
            identificacion
        )

        try:
            hash_contrasena = calcular_hash_validado(
                contrasena, identificacion=identificacion
            )
        except ErrorDePolitica as error:
            print(f"La contraseña no cumple la política: {error}", file=sys.stderr)
            return 1

        repetida = sesion_bd.scalar(
            select(Usuario).where(Usuario.identificacion == identificacion)
        )
        if repetida is not None:
            print(
                f"Ya existe un usuario con la identificación {identificacion}. "
                "Si debe ser Administrador, cámbiale el rol desde la plataforma.",
                file=sys.stderr,
            )
            return 1

        sesion_bd.add(
            Usuario(
                identificacion=identificacion,
                hash_contrasena=hash_contrasena,
                rol=Rol.ADMINISTRADOR,
                activo=True,
            )
        )
        sesion_bd.commit()

    # Se confirma la identificación, nunca la contraseña.
    print(f"Administrador inicial creado: {identificacion}")
    return 0


if __name__ == "__main__":
    raise SystemExit(crear_administrador_inicial())
