"""Conexión a la base de datos.

La cadena de conexión sale de configuración (RF-23); aquí no hay credenciales.
"""

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.configuracion import obtener_configuracion


class Base(DeclarativeBase):
    """Base común de los modelos. Alembic toma de aquí el esquema."""


_configuracion = obtener_configuracion()

motor = create_engine(_configuracion.bd_url, pool_pre_ping=True, future=True)

FabricaDeSesiones = sessionmaker(bind=motor, autoflush=False, expire_on_commit=False)


def obtener_sesion_bd() -> Iterator[Session]:
    """Entrega una sesión de base de datos por petición y la cierra al final."""
    sesion = FabricaDeSesiones()
    try:
        yield sesion
    finally:
        sesion.close()
