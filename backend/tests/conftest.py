"""Andamiaje de las pruebas del backend.

Las pruebas corren contra una base de datos aparte, derivada de `VIDA_BD_URL`
agregándole el sufijo `_pruebas`, para no tocar nunca los datos de desarrollo.
Se crea sola si no existe. Cada prueba corre en su propia transacción, que se
revierte al terminar.
"""

from collections.abc import Iterator
from pathlib import Path

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


# ---------------------------------------------------------------------------
# Apoyos de la funcionalidad 002 — tipos de documentación
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def formatos_de_prueba(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    """Los cuatro formatos ficticios, generados una vez por sesión.

    Se generan y no se versionan: en el repositorio no hay binarios, y el
    formato real del cliente no entra (Art. X.3).
    """
    from scripts.generar_formatos_de_prueba import generar_todos

    return generar_todos(tmp_path_factory.mktemp("formatos"))


@pytest.fixture
def estructuras_esperadas() -> dict[str, dict]:
    """La estructura que cada formato de prueba debe producir, como dato.

    Vive al lado del generador y no de la prueba: comparar contra este
    diccionario es lo que hace del Art. II algo verificable en vez de una
    opinión de quien escribe la prueba.
    """
    from scripts import generar_formatos_de_prueba as generador

    return {
        "referencia": generador.ESTRUCTURA_REFERENCIA,
        "generalizacion_word": generador.ESTRUCTURA_GENERALIZACION,
        "generalizacion_excel": generador.ESTRUCTURA_EXCEL,
        "solo_negritas": generador.ESTRUCTURA_SOLO_NEGRITAS_LEIDA,
    }


@pytest.fixture
def almacen_temporal(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[Path]:
    """Apunta el almacén de formatos a una carpeta temporal.

    Sin esto las pruebas escribirían en `uploads/`, que es el almacén de
    desarrollo: una prueba no debe dejar archivos donde el desarrollador tiene
    los suyos.
    """
    carpeta = tmp_path / "almacen"
    monkeypatch.setenv("VIDA_ALMACEN_FORMATOS", str(carpeta))
    # La configuración está memorizada: sin limpiar la memoria, la variable
    # recién puesta no la ve nadie.
    obtener_configuracion.cache_clear()
    try:
        yield carpeta
    finally:
        obtener_configuracion.cache_clear()


@pytest.fixture
def litellm_fijo(monkeypatch: pytest.MonkeyPatch):
    """Sustituye la consulta a LiteLLM por una respuesta fija.

    **Ninguna prueba del repositorio sale a la red.** El respaldo con IA se
    prueba con esta sustitución: lo que se verifica es el descarte de RF-05d y
    que la lectura directa tenga prioridad, no que el modelo acierte.

    La costura es `propuesta_ia.consultar_litellm(mensaje: str) -> str`, la
    única función de la funcionalidad que hace una petición HTTP. Está
    declarada aquí porque el apoyo se escribe antes que el módulo (fase 3
    antes que fase 5): T018b debe exponer ese nombre.

    Devuelve un registrador para que la prueba compruebe **cuántas veces** se
    llamó. Que sean cero con un formato bien marcado es lo que verifica el
    Art. VI.
    """

    class ConsultaSustituida:
        def __init__(self) -> None:
            self.respuesta = "{}"
            self.llamadas: list[str] = []
            self.falla: Exception | None = None

        def __call__(self, mensaje: str) -> str:
            self.llamadas.append(mensaje)
            if self.falla is not None:
                raise self.falla
            return self.respuesta

        @property
        def veces(self) -> int:
            return len(self.llamadas)

    sustituta = ConsultaSustituida()
    # Falla ruidosamente si `propuesta_ia` deja de exponer `consultar_litellm`.
    # Es a propósito: si esa costura cambia de nombre, lo que no se quiere es
    # que las pruebas del respaldo pasen porque ya no sustituyen nada y
    # empiecen a salir a la red de verdad.
    monkeypatch.setattr("app.formatos.propuesta_ia.consultar_litellm", sustituta)
    return sustituta
