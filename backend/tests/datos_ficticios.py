"""Usuarios ficticios para las pruebas de acceso y roles.

Ninguno corresponde a una persona real: identificaciones del dominio
`ejemplo.local`, reservado para ejemplos, y contraseñas inventadas que no se
usan en ninguna parte (Art. X.3 de la constitución).

Los cinco cubren las cinco situaciones de acceso de la sección 8 de la spec:
RO activo, Administrador activo, segundo Administrador, usuario autenticado
sin rol y usuario con el acceso revocado.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class UsuarioFicticio:
    """Un usuario de prueba y el estado en que debe quedar sembrado."""

    identificacion: str
    contrasena: str
    rol: str | None
    activo: bool
    descripcion: str


# Contraseñas de prueba: largas, inventadas y fuera de la lista de comunes,
# para que pasen la política vigente (RF-20) sin depender de sus valores.
RO = UsuarioFicticio(
    identificacion="ro.prueba@ejemplo.local",
    contrasena="prueba-ro-acceso-7318",
    rol="RO",
    activo=True,
    descripcion="RO activo: usa la plataforma y no administra nada",
)

ADMINISTRADOR = UsuarioFicticio(
    identificacion="admin.prueba@ejemplo.local",
    contrasena="prueba-admin-acceso-9542",
    rol="ADMINISTRADOR",
    activo=True,
    descripcion="Administrador activo: hace todo lo del RO y administra usuarios",
)

SEGUNDO_ADMINISTRADOR = UsuarioFicticio(
    identificacion="admin.segundo@ejemplo.local",
    contrasena="prueba-admin-segundo-4176",
    rol="ADMINISTRADOR",
    activo=True,
    descripcion=(
        "Segundo Administrador: permite probar las acciones sobre un "
        "Administrador sin dejar la plataforma sin ninguno (RF-16)"
    ),
)

SIN_ROL = UsuarioFicticio(
    identificacion="sinrol.prueba@ejemplo.local",
    contrasena="prueba-sinrol-acceso-2869",
    rol=None,
    activo=True,
    descripcion="Se identifica bien pero no tiene rol asignado: no entra (RF-06)",
)

REVOCADO = UsuarioFicticio(
    identificacion="revocado.prueba@ejemplo.local",
    contrasena="prueba-revocado-acceso-6035",
    rol="RO",
    activo=False,
    descripcion="Tenía acceso y se le revocó: no entra (RF-15)",
)

TODOS = (RO, ADMINISTRADOR, SEGUNDO_ADMINISTRADOR, SIN_ROL, REVOCADO)

# Identificación que no existe en la base, para probar que el mensaje de
# acceso negado es el mismo que cuando el usuario sí existe (RF-09).
INEXISTENTE = "nadie@ejemplo.local"

# Contraseña equivocada, para los casos negativos.
CONTRASENA_EQUIVOCADA = "esta-no-es-la-contrasena-5120"
