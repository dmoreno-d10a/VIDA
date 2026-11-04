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

    # --- Documentación interactiva de la API ---
    # Apagada por omisión: /docs, /redoc y /openapi.json describen la
    # superficie de la API y RF-01 no admite contenido accesible sin sesión.
    # Se puede encender en desarrollo con VIDA_DOCS_API=1.
    docs_api: bool = Field(default=False)

    # --- Formatos de los tipos de documentacion (spec 002, RF-18) ---
    # Los tres son configurables a proposito: cambiar las extensiones
    # admitidas o el tamano maximo no debe exigir tocar codigo (CE-08).
    almacen_formatos: Path = Field(default=Path("uploads/formatos"))
    formato_mb_max: int = Field(default=25, gt=0)
    formato_extensiones: str = Field(default="docx,xlsx")

    # --- Respaldo con IA del reconocimiento (spec 002, RF-05c) ---
    # Cuando la lectura del archivo no reconoce ninguna estructura, se le pide
    # a la IA que proponga una y el Administrador la confirma. El interruptor
    # permite operar sin VORKAN: apagado, ese formato se rechaza.
    #
    # `modelo_reconocimiento` nombra una TAREA de LiteLLM, no un modelo: qué
    # modelo la atiende se configura allá, y elegirlo es de la 007 (Art. V).
    ia_respaldo: bool = Field(default=True)
    litellm_url: str = Field(default="http://localhost:4000")
    litellm_api_key: str | None = Field(default=None)
    modelo_reconocimiento: str = Field(default="reconocimiento-de-formato")

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


    @property
    def ruta_almacen_formatos(self) -> Path:
        """Ruta absoluta de la carpeta donde se guardan los archivos de formato.

        La ruta configurada es relativa a la raiz del repositorio, no a
        `backend/`: el almacen vive en `uploads/`, que `.gitignore` excluye,
        asi que ningun archivo cargado puede llegar al repositorio (Art. X.2).
        """
        if self.almacen_formatos.is_absolute():
            return self.almacen_formatos
        return RAIZ_REPOSITORIO / self.almacen_formatos

    @property
    def formato_tamano_max_bytes(self) -> int:
        """El limite de RF-18 en bytes, que es como lo necesita la carga."""
        return self.formato_mb_max * 1024 * 1024

    @property
    def respaldo_ia_disponible(self) -> bool:
        """Si el respaldo con IA se puede intentar en esta instalación.

        Sin credencial no hay a quién preguntarle, así que vale lo mismo que
        tenerlo apagado: la carga de un formato sin estructura reconocible se
        rechaza (RF-10) en vez de fallar a medias.
        """
        return self.ia_respaldo and bool(self.litellm_api_key)

    @property
    def extensiones_admitidas(self) -> tuple[str, ...]:
        """Las extensiones de RF-04, en minusculas y sin punto.

        Se admite escribirlas con o sin punto y con espacios de sobra: lo que
        el Administrador configure se normaliza aqui, una sola vez.
        """
        partes = (
            parte.strip().lstrip(".").lower()
            for parte in self.formato_extensiones.split(",")
        )
        return tuple(parte for parte in partes if parte)


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
