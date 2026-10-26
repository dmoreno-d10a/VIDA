"""Arranque del backend de V.I.D.A.

Esta capa concentra la lógica y las credenciales: el front no contiene
ninguna de las dos (Art. IV de la constitución).
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as ErrorHTTP

from app.configuracion import obtener_configuracion
from app.rutas import acceso

# Se lee al importar para que una configuración incompleta impida el arranque,
# en vez de descubrirse en la primera petición (RF-23).
configuracion = obtener_configuracion()

app = FastAPI(
    title="V.I.D.A. — API",
    description=(
        "Backend de la plataforma V.I.D.A. "
        "Vortexbird Intelligent Documentation Assistant."
    ),
    version="0.1.0",
)


@app.exception_handler(ErrorHTTP)
async def manejar_error_http(_: Request, error: ErrorHTTP) -> JSONResponse:
    """Responde los errores con la clave `detalle`, en español (Art. XII)."""
    return JSONResponse(
        status_code=error.status_code,
        content={"detalle": error.detail},
        headers=getattr(error, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def manejar_error_de_validacion(
    _: Request, error: RequestValidationError
) -> JSONResponse:
    """Traduce los errores de validación a un mensaje único, en español.

    No se devuelve el detalle crudo de la validación: en una creación de
    usuario eso incluiría los datos enviados, y entre ellos la contraseña
    (RF-19).
    """
    campos = sorted(
        {
            str(parte)
            for detalle in error.errors()
            for parte in detalle["loc"][1:]
            if isinstance(parte, str)
        }
    )
    mensaje = "Los datos enviados no son válidos."
    if campos:
        mensaje += " Revisa: " + ", ".join(campos) + "."
    return JSONResponse(status_code=422, content={"detalle": mensaje})


app.include_router(acceso.enrutador)


@app.get("/salud", tags=["salud"])
def salud() -> dict[str, str]:
    """Indica que el backend está arriba y atendiendo peticiones.

    Es la única ruta sin sesión, y por eso no devuelve ningún dato de la
    plataforma: solo dice que responde.
    """
    return {"estado": "ok"}
