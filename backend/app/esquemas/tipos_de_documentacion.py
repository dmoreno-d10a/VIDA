"""Esquemas de los tipos de documentación (HU-1 a HU-5).

La forma exacta de cada respuesta está en
[`contracts/api-tipos-de-documentacion.md`](../../../specs/002-tipos-de-documentacion/contracts/api-tipos-de-documentacion.md).

`estructura` se declara como `dict` y no con un modelo por clase de formato a
propósito. El JSON que se guarda tiene una forma por clase (`word`, `excel`) y
el Art. I dice que esa forma la define el archivo, no la plataforma: validarla
aquí con un modelo cerrado obligaría a cambiar código cada vez que aparezca
una clase de formato nueva. Lo que sí se verifica es lo que importa —que nada
se inventó—, y eso lo hace el reconocimiento, no el esquema.
"""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class NuevoTipo(BaseModel):
    """Lo que envía el Administrador para crear un tipo (RF-01, RF-02)."""

    nombre: str = Field(min_length=1, max_length=200)
    descripcion: str | None = Field(default=None, max_length=1000)

    @field_validator("nombre")
    @classmethod
    def _nombre_no_vacio(cls, valor: str) -> str:
        """Un nombre de solo espacios no es un nombre (RF-02a).

        El valor **no** se normaliza: se devuelve tal como lo escribió el
        Administrador (Art. II). Lo único que se rechaza es que no quede nada
        al quitarle los espacios.
        """
        if not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        return valor

    @field_validator("descripcion")
    @classmethod
    def _descripcion_vacia_es_ninguna(cls, valor: str | None) -> str | None:
        """Una descripción de solo espacios se guarda como ausente.

        Así «sin descripción» es un solo estado en la base de datos y no dos
        que se ven igual en pantalla.
        """
        if valor is not None and not valor.strip():
            return None
        return valor


class CambioDeTipo(BaseModel):
    """Nombre y descripción nuevos (RF-12). Los dos son opcionales.

    No toca la estructura reconocida: corregir el nombre de un tipo no tiene
    por qué volver a analizar su formato.
    """

    nombre: str | None = Field(default=None, min_length=1, max_length=200)
    descripcion: str | None = Field(default=None, max_length=1000)

    @field_validator("nombre")
    @classmethod
    def _nombre_no_vacio(cls, valor: str | None) -> str | None:
        if valor is not None and not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        return valor


class CambioDeActivacion(BaseModel):
    """Si el tipo queda desactivado o vuelve a circulación (RF-14)."""

    desactivado: bool


class VersionEnListado(BaseModel):
    """La versión vigente, como se ve en el listado de tipos."""

    numero: int
    extension: str
    creado_en: datetime

    model_config = {"from_attributes": True}


class TipoEnListado(BaseModel):
    """Una fila del listado de tipos (RF-03)."""

    id: int
    nombre: str
    descripcion: str | None
    # Es la propiedad derivada del modelo, no una columna.
    estado: str
    version_vigente: VersionEnListado | None

    model_config = {"from_attributes": True}


class VersionConEstructura(BaseModel):
    """Una versión con su estructura completa (RF-08, RF-21)."""

    numero: int
    nombre_archivo_original: str
    extension: str
    tamano_bytes: int
    creado_en: datetime
    estructura: dict

    model_config = {"from_attributes": True}


class VersionEnHistorial(BaseModel):
    """Una entrada del historial, **sin** la estructura (RF-21).

    La estructura de las versiones anteriores se pide por su propia ruta: si
    viniera aquí, el detalle de un tipo con muchas versiones crecería sin
    límite.
    """

    numero: int
    nombre_archivo_original: str
    creado_en: datetime
    vigente: bool

    model_config = {"from_attributes": True}


class DetalleDeTipo(BaseModel):
    """El detalle que el Administrador usa para comparar con su archivo (RF-08)."""

    id: int
    nombre: str
    descripcion: str | None
    estado: str
    version_vigente: VersionConEstructura | None
    historial: list[VersionEnHistorial]

    model_config = {"from_attributes": True}


class TipoDisponible(BaseModel):
    """Un tipo activo, como lo ve un RO (RF-16).

    Nada más que lo necesario para elegir: ni estructura, ni historial, ni
    estado. Lo que no está en el esquema no se puede filtrar por accidente.
    """

    id: int
    nombre: str
    descripcion: str | None

    model_config = {"from_attributes": True}
