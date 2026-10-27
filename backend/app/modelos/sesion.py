"""Modelo de sesión.

La sesión vive en la base de datos y la cookie solo lleva un identificador
opaco. Se eligió así para que revocar o eliminar un usuario le quite el acceso
de inmediato, sin esperar a que nada expire (RF-07, RF-15).
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, delete, func
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from app.bd import Base
from app.modelos.usuario import Usuario


class SesionUsuario(Base):
    """Una sesión abierta por un usuario."""

    __tablename__ = "sesion_usuario"

    # Identificador opaco, generado al azar. Es lo único que viaja en la
    # cookie: no lleva dentro ningún dato del usuario.
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuario.id", ondelete="CASCADE"), index=True, nullable=False
    )

    creada_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    expira_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    usuario: Mapped[Usuario] = relationship(lazy="joined")

    def __repr__(self) -> str:
        return f"<SesionUsuario de usuario {self.usuario_id}, expira {self.expira_en}>"


def terminar_sesiones_de(sesion_bd: Session, usuario_id: int) -> int:
    """Termina todas las sesiones abiertas de un usuario, en una operación.

    Se usa al revocar el acceso, al eliminar la cuenta y al restablecer la
    contraseña: en los tres casos, lo que ya estaba abierto deja de servir.
    Devuelve cuántas sesiones se terminaron.
    """
    resultado = sesion_bd.execute(
        delete(SesionUsuario).where(SesionUsuario.usuario_id == usuario_id)
    )
    return resultado.rowcount or 0
