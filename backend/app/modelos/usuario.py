"""Modelo de usuario.

Guarda quién puede entrar y con qué rol. **Nunca** guarda la contraseña: solo
su hash, que no es reversible (RF-19).
"""

import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.bd import Base


class Rol(enum.Enum):
    """Los dos únicos roles de la plataforma (RF-02).

    No hay más, ni permisos por usuario: el Administrador puede hacer todo lo
    que hace un RO, y además administrar.
    """

    RO = "RO"
    ADMINISTRADOR = "ADMINISTRADOR"


class Usuario(Base):
    """Un usuario de V.I.D.A."""

    __tablename__ = "usuario"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # La identificación es única: no pueden existir dos usuarios con la misma
    # (RF-12). Se guarda tal como la escribió el Administrador.
    identificacion: Mapped[str] = mapped_column(String(320), unique=True, index=True)

    # Hash Argon2id. No existe ninguna columna con la contraseña legible.
    hash_contrasena: Mapped[str] = mapped_column(String(255))

    # Puede faltar: un usuario sin rol no entra y no recibe ningún rol por
    # omisión (RF-06, Art. II).
    rol: Mapped[Rol | None] = mapped_column(
        Enum(Rol, name="rol_usuario", native_enum=False, length=20),
        nullable=True,
        default=None,
    )

    # Estado del acceso: revocarlo no borra al usuario (RF-15).
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Bloqueo temporal por intentos fallidos (RF-22). El bloqueo se levanta
    # por tiempo: no hay que desbloquear a mano.
    intentos_fallidos: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    bloqueado_hasta: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        """Representación sin dato sensible alguno."""
        rol = self.rol.value if self.rol else "sin rol"
        return f"<Usuario {self.identificacion} ({rol}, {'activo' if self.activo else 'revocado'})>"
