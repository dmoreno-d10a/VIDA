"""Esquemas de la administración de usuarios (HU-5, RF-11 a RF-16)."""

from pydantic import BaseModel, Field

from app.modelos.usuario import Rol


class UsuarioEnListado(BaseModel):
    """Una fila del listado: identificación, rol y estado del acceso (RF-11).

    No existe ningún campo de contraseña, ni el hash: el Administrador
    tampoco puede verla (RF-19).
    """

    id: int
    identificacion: str
    rol: Rol | None
    activo: bool

    model_config = {"from_attributes": True, "use_enum_values": True}


class NuevoUsuario(BaseModel):
    """Lo que envía el Administrador para crear un usuario (RF-12)."""

    identificacion: str = Field(min_length=1, max_length=320)
    rol: Rol
    contrasena: str = Field(min_length=1, max_length=512)


class CambioDeRol(BaseModel):
    """Rol al que pasa un usuario existente (RF-13)."""

    rol: Rol


class ContrasenaRestablecida(BaseModel):
    """Contraseña que el Administrador le define a un usuario (RF-14)."""

    contrasena: str = Field(min_length=1, max_length=512)


class CambioDeAcceso(BaseModel):
    """Si el acceso del usuario queda activo o revocado (RF-15)."""

    activo: bool
