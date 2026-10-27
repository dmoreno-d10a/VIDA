"""Andamiaje de las pruebas del backend.

Las pruebas corren contra una base de datos aparte, derivada de `VIDA_BD_URL`
agregándole el sufijo `_pruebas`, para no tocar nunca los datos de desarrollo.
Se crea sola si no existe. Cada prueba corre en su propia transacción, que se
revierte al terminar.
"""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine, make_url
from sqlalchemy.orm import Session, sessionmaker

from app.bd import Base, obtener_sesion_bd
from app.configuracion import obtener_configuracion


def _como_texto(url: URL) -> str:
    """Convierte la URL a texto **con** la contraseña.

    `str(url)` la enmascara con `***`, lo que produce una cadena que parece
    correcta y falla al conectarse.
    """
    return url.render_as_string(hide_password=False)


def _url_de_pruebas() -> str:
    """Devuelve la URL de la base de pruebas, derivada de la de desarrollo."""
    url = make_url(obtener_configuracion().bd_url)
    nombre = (url.database or "vida") + "_pruebas"
    return _como_texto(url.set(database=nombre))


def _crear_base_si_falta(url_pruebas: str) -> None:
    """Crea la base de pruebas si todavía no existe."""
    url = make_url(url_pruebas)
    nombre = url.database
    administrativa = create_engine(
        _como_texto(url.set(database="postgres")), isolation_level="AUTOCOMMIT"
    )
    with administrativa.connect() as conexion:
        existe = conexion.execute(
            text("select 1 from pg_database where datname = :nombre"),
            {"nombre": nombre},
        ).scalar()
        if not existe:
            conexion.execute(text(f'create database "{nombre}"'))
    administrativa.dispose()


@pytest.fixture(scope="session")
def motor_pruebas() -> Iterator[Engine]:
    """Motor contra la base de pruebas, con el esquema ya creado."""
    url = _url_de_pruebas()
    _crear_base_si_falta(url)
    motor = create_engine(url, future=True)

    # Importa los modelos para que `Base.metadata` tenga todas las tablas.
    import app.modelos  # noqa: F401

    Base.metadata.create_all(motor)
    yield motor
    motor.dispose()


@pytest.fixture
def sesion_bd(motor_pruebas: Engine) -> Iterator[Session]:
    """Sesión dentro de una transacción que se revierte al terminar la prueba."""
    conexion = motor_pruebas.connect()
    transaccion = conexion.begin()
    # join_transaction_mode="create_savepoint": los commit() de las rutas se
    # vuelven savepoints, así que la transacción externa sigue pudiendo
    # revertir todo lo que hizo la prueba.
    sesion = sessionmaker(
        bind=conexion,
        autoflush=False,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )()
    try:
        yield sesion
    finally:
        sesion.close()
        transaccion.rollback()
        conexion.close()


@pytest.fixture
def cliente(sesion_bd: Session) -> Iterator[TestClient]:
    """Cliente HTTP del backend, usando la sesión de pruebas."""
    from app.main import app

    app.dependency_overrides[obtener_sesion_bd] = lambda: sesion_bd
    with TestClient(app) as cliente_http:
        yield cliente_http
    app.dependency_overrides.clear()


@pytest.fixture
def usuarios(sesion_bd: Session) -> dict[str, object]:
    """Siembra los cinco usuarios ficticios y los devuelve por identificación.

    Importa el modelo dentro de la función a propósito: así el andamiaje se
    puede escribir antes de que el modelo exista, y las pruebas que dependen
    de él fallan —como corresponde en esta fase— en vez de romper la
    recolección de todas las pruebas.
    """
    from app.modelos.usuario import Rol, Usuario
    from app.seguridad.contrasena import calcular_hash

    from tests import datos_ficticios

    creados: dict[str, object] = {}
    for ficticio in datos_ficticios.TODOS:
        usuario = Usuario(
            identificacion=ficticio.identificacion,
            hash_contrasena=calcular_hash(ficticio.contrasena),
            rol=Rol(ficticio.rol) if ficticio.rol else None,
            activo=ficticio.activo,
        )
        sesion_bd.add(usuario)
        creados[ficticio.identificacion] = usuario
    sesion_bd.flush()
    return creados
