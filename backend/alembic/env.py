"""Entorno de migraciones de V.I.D.A.

La cadena de conexión sale de `app.configuracion`, nunca de `alembic.ini`:
en el repositorio no se guardan credenciales (Art. X.2).
"""

from logging.config import fileConfig

from alembic import context

from app.bd import Base, motor

# Los modelos deben importarse para que Alembic vea sus tablas.
# (se agregan a medida que las tareas los crean)
import app.modelos  # noqa: F401

configuracion_alembic = context.config

if configuracion_alembic.config_file_name is not None:
    fileConfig(configuracion_alembic.config_file_name)

metadatos_objetivo = Base.metadata


def migrar_sin_conexion() -> None:
    """Genera el SQL de la migración sin conectarse a la base."""
    context.configure(
        url=str(motor.url),
        target_metadata=metadatos_objetivo,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def migrar_con_conexion() -> None:
    """Aplica la migración contra la base de datos configurada."""
    with motor.connect() as conexion:
        context.configure(
            connection=conexion,
            target_metadata=metadatos_objetivo,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    migrar_sin_conexion()
else:
    migrar_con_conexion()
