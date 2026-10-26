"""Arranque del backend de V.I.D.A.

Esta capa concentra la lógica y las credenciales: el front no contiene
ninguna de las dos (Art. IV de la constitución).
"""

from fastapi import FastAPI

from app.configuracion import obtener_configuracion

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


@app.get("/salud", tags=["salud"])
def salud() -> dict[str, str]:
    """Indica que el backend está arriba y atendiendo peticiones."""
    return {"estado": "ok"}
