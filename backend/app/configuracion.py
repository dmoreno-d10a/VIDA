"""Configuración del backend de V.I.D.A.

Todos los parámetros se leen del entorno. Ninguno queda escrito en el código
(RF-23): cambiar la duración de la sesión, la política de contraseñas o el
bloqueo por intentos fallidos no exige tocar ni una línea.

Los parámetros sin valor por defecto hacen fallar el arranque si faltan, en
vez de asumir algo por su cuenta (Art. II).
"""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, ValidationError, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# El `.env` vive en la raíz del repositorio, un nivel arriba de `backend/`.
RAIZ_BACKEND = Path(__file__).resolve().parent.parent
RAIZ_REPOSITORIO = RAIZ_BACKEND.parent


class ErrorDeConfiguracion(RuntimeError):
    """Falta configuración obligatoria o alguno de los valores no es válido."""


class Configuracion(BaseSettings):
    """Parámetros de ejecución, todos con prefijo `VIDA_` en el entorno."""

    model_config = SettingsConfigDict(
        env_prefix="VIDA_",
        env_file=(RAIZ_REPOSITORIO / ".env", RAIZ_BACKEND / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Base de datos. Sin valor por defecto: sin esto no hay plataforma. ---
    bd_url: str = Field(description="Cadena de conexión a PostgreSQL")

    # --- Sesión (RF-07) ---
    sesion_minutos: int = Field(default=480, gt=0)

    # --- Política de contraseñas (RF-20) ---
    contrasena_min: int = Field(default=12, gt=0)
    contrasena_max: int = Field(default=64, gt=0)
    contrasenas_comunes: Path = Field(default=Path("app/datos/contrasenas-comunes.txt"))

    # --- Bloqueo por intentos fallidos (RF-22) ---
    intentos_max: int = Field(default=5, gt=0)
    bloqueo_minutos: int = Field(default=15, gt=0)

    # --- Administrador inicial (RF-18). Solo se usan en la puesta en marcha. ---
    admin_inicial: str | None = Field(default=None)
    admin_inicial_contrasena: str | None = Field(default=None)

    @model_validator(mode="after")
    def _validar_rango_de_contrasena(self) -> "Configuracion":
        if self.contrasena_min > self.contrasena_max:
            raise ValueError(
                "VIDA_CONTRASENA_MIN no puede ser mayor que VIDA_CONTRASENA_MAX"
            )
        return self

    @property
    def ruta_contrasenas_comunes(self) -> Path:
        """Ruta absoluta de la lista de contraseñas comunes."""
        if self.contrasenas_comunes.is_absolute():
            return self.contrasenas_comunes
        return RAIZ_BACKEND / self.contrasenas_comunes


def _mensaje_de_error(error: ValidationError) -> str:
    """Traduce el error de validación a un mensaje accionable, en español."""
    faltantes: list[str] = []
    invalidos: list[str] = []

    for detalle in error.errors():
        campo = str(detalle["loc"][0]) if detalle["loc"] else ""
        variable = f"VIDA_{campo.upper()}" if campo else "(configuración)"
        if detalle["type"] == "missing":
            faltantes.append(variable)
        else:
            invalidos.append(f"{variable}: {detalle['msg']}")

    partes = ["No se pudo leer la configuración de V.I.D.A."]
    if faltantes:
        partes.append(
            "Faltan estas variables de entorno obligatorias: "
            + ", ".join(sorted(faltantes))
        )
    if invalidos:
        partes.append("Valores no válidos: " + "; ".join(invalidos))
    partes.append("Copia .env.ejemplo a .env y define los valores que falten.")
    return " ".join(partes)


@lru_cache
def obtener_configuracion() -> Configuracion:
    """Devuelve la configuración leída del entorno.

    Lanza `ErrorDeConfiguracion` si falta algo obligatorio, de modo que el
    backend no arranque a medias.
    """
    try:
        return Configuracion()  # type: ignore[call-arg]
    except ValidationError as error:
        raise ErrorDeConfiguracion(_mensaje_de_error(error)) from error
