"""Esquemas de acceso.

Regla que vale para todo este archivo: una contraseña puede **entrar** en un
esquema, nunca salir (RF-19).
"""

from pydantic import BaseModel, Field

from app.modelos.usuario import Rol


class SolicitudDeAcceso(BaseModel):
    """Lo que envía quien quiere entrar."""

    identificacion: str = Field(min_length=1, max_length=320)
    contrasena: str = Field(min_length=1, max_length=512)


class SesionActual(BaseModel):
    """Quién es el usuario y con qué rol entró (HU-4, RF-08)."""

    identificacion: str
    rol: Rol

    model_config = {"from_attributes": True, "use_enum_values": True}


class CambioDeContrasenaPropia(BaseModel):
    """Lo que envía el usuario para cambiar su propia contraseña (HU-6)."""

    contrasena_actual: str = Field(min_length=1, max_length=512)
    contrasena_nueva: str = Field(min_length=1, max_length=512)
