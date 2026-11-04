"""El respaldo con IA: propone la estructura cuando la lectura no reconoce nada.

Es el **único** archivo de la funcionalidad 002 que sale a la red. Habla con
LiteLLM por HTTP y no con el SDK de ningún proveedor: eso es lo que lo hace
intercambiable (Art. V). Dirección, credencial y nombre de la tarea salen de
la configuración; aquí no hay ningún modelo escrito.

`VIDA_MODELO_RECONOCIMIENTO` nombra una **tarea** de LiteLLM, no un modelo:
qué modelo la atiende se configura allá, y elegirlo es de la funcionalidad 007.

Las dos reglas que hacen que esto no contradiga el Art. II:

1. Solo se manda el **esqueleto** del documento, nunca el archivo (Art. VI).
2. Todo nombre propuesto que no aparezca **literalmente** en el documento se
   **descarta**, sin reemplazarlo por nada (RF-05d). Es una comparación de
   cadenas, no una política: una prueba puede afirmarlo.

Cuando no hay propuesta —el respaldo está apagado, no hay credencial, LiteLLM
no responde, responde algo que no se entiende, o no queda nada tras el
descarte— este módulo devuelve `None`. **No** levanta excepciones hacia
afuera: para el Administrador las cinco situaciones son la misma, y el
contrato les da un solo mensaje.
"""

import json
import logging

import httpx

from app.configuracion import obtener_configuracion
from app.formatos.texto_para_ia import EsqueletoDelDocumento

registro = logging.getLogger(__name__)

# Menor que el techo de 30 s de la carga completa (CE-09), con margen para
# escribir el archivo, leerlo y responder. Si LiteLLM tarda más que esto, la
# carga se rechaza en vez de hacer esperar al Administrador hasta el techo.
LIMITE_DE_ESPERA_SEGUNDOS = 20.0

INSTRUCCION = """\
Eres un analista que identifica la estructura de un formato de documento.

Vas a recibir el esqueleto de un documento: sus párrafos en orden, cada uno \
con las señales de forma que trae (negrita, tamaño de letra, si es corto), o \
las hojas de un libro con sus primeras filas.

Tu tarea es decir **qué secciones tiene el documento**, es decir, qué habría \
que llenar para producir uno igual. No resumas el contenido y no propongas \
secciones que el documento no tenga.

Reglas que no puedes romper:

- Cada nombre que propongas debe aparecer **tal cual**, carácter por carácter, \
en el esqueleto que recibiste. No lo corrijas, no lo traduzcas, no lo \
completes y no le cambies las mayúsculas.
- Si no reconoces ninguna estructura, responde con la lista vacía.

Responde **solo** con un objeto JSON, sin texto alrededor:

Para un documento de Word:
{"clase": "word", "secciones": [{"nombre": "...", "nivel": 1}]}

Para un libro de Excel:
{"clase": "excel", "hojas": [{"nombre": "...", "fila_de_encabezados": 1, \
"columnas": ["..."]}]}
"""


class SinPropuesta(Exception):
    """Interno: no hay propuesta utilizable. No sale de este módulo."""


def consultar_litellm(mensaje: str) -> str:
    """Le pide a LiteLLM la propuesta y devuelve su respuesta en texto.

    Es la **única** función de la funcionalidad que hace una petición HTTP, y
    la costura que las pruebas sustituyen para que ninguna salga a la red.
    """
    configuracion = obtener_configuracion()

    respuesta = httpx.post(
        f"{configuracion.litellm_url.rstrip('/')}/v1/chat/completions",
        headers={"Authorization": f"Bearer {configuracion.litellm_api_key}"},
        json={
            "model": configuracion.modelo_reconocimiento,
            "messages": [
                {"role": "system", "content": INSTRUCCION},
                {"role": "user", "content": mensaje},
            ],
            # La respuesta tiene que ser un JSON que se pueda interpretar; no
            # se le pide creatividad a un trabajo de reconocimiento.
            "temperature": 0,
        },
        timeout=LIMITE_DE_ESPERA_SEGUNDOS,
    )
    respuesta.raise_for_status()
    return respuesta.json()["choices"][0]["message"]["content"]


def _interpretar(texto: str) -> dict:
    """Saca el objeto JSON de la respuesta del modelo."""
    recortado = texto.strip()
    # Algunos modelos envuelven el JSON en un bloque de código aunque se les
    # pida que no. Quitarlo es más barato que descartar la propuesta entera.
    if recortado.startswith("```"):
        recortado = recortado.split("```")[1]
        if recortado.startswith("json"):
            recortado = recortado[4:]
    try:
        propuesta = json.loads(recortado.strip())
    except (ValueError, IndexError) as error:
        raise SinPropuesta("La respuesta no es un JSON interpretable.") from error
    if not isinstance(propuesta, dict):
        raise SinPropuesta("La respuesta no es un objeto.")
    return propuesta


def _depurar(propuesta: dict, literales: list[str]) -> dict | None:
    """Descarta todo nombre que no esté literalmente en el documento (RF-05d).

    Lo descartado no se reemplaza por nada ni se anota: lo que no entró, no
    existió. Devuelve `None` si tras el descarte no queda nada.
    """
    permitidos = set(literales)
    clase = propuesta.get("clase")

    if clase == "word":
        secciones = []
        for seccion in propuesta.get("secciones") or []:
            if not isinstance(seccion, dict):
                continue
            nombre = seccion.get("nombre")
            if not isinstance(nombre, str) or nombre not in permitidos:
                continue
            nivel = seccion.get("nivel")
            secciones.append(
                {"nombre": nombre, "nivel": nivel if isinstance(nivel, int) else 1}
            )
        return {"clase": "word", "secciones": secciones} if secciones else None

    if clase == "excel":
        hojas = []
        for hoja in propuesta.get("hojas") or []:
            if not isinstance(hoja, dict):
                continue
            nombre = hoja.get("nombre")
            if not isinstance(nombre, str) or nombre not in permitidos:
                continue
            columnas = [
                columna
                for columna in (hoja.get("columnas") or [])
                if isinstance(columna, str) and columna in permitidos
            ]
            fila = hoja.get("fila_de_encabezados")
            hojas.append(
                {
                    "nombre": nombre,
                    "fila_de_encabezados": fila if isinstance(fila, int) else None,
                    "columnas": columnas,
                }
            )
        # La misma regla que la lectura directa: un libro sin una sola columna
        # no sirve para generar nada.
        if any(hoja["columnas"] for hoja in hojas):
            return {"clase": "excel", "hojas": hojas}
        return None

    raise SinPropuesta(f"Clase de formato desconocida: {clase!r}.")


def proponer(esqueleto: EsqueletoDelDocumento) -> dict | None:
    """La estructura propuesta, o `None` si no hay ninguna utilizable.

    Nunca levanta: las cinco formas de no tener propuesta son la misma para
    quien llama.
    """
    configuracion = obtener_configuracion()
    if not configuracion.respaldo_ia_disponible:
        # Sin interruptor o sin credencial no hay a quién preguntarle. No se
        # intenta la llamada, así que no cuesta nada.
        registro.info(
            "El respaldo con IA está indisponible; el formato se rechaza sin consultar."
        )
        return None

    if not esqueleto.descripcion.strip():
        # Un archivo que se abrió pero no tiene ni un párrafo con texto no
        # tiene nada que mandar, y mandar un esqueleto vacío solo gastaría una
        # llamada para que el modelo invente.
        registro.info("El documento no tiene texto que mandar; no se consulta la IA.")
        return None

    try:
        respuesta = consultar_litellm(esqueleto.descripcion)
        propuesta = _depurar(_interpretar(respuesta), esqueleto.textos_literales)
    except SinPropuesta as error:
        registro.warning("La propuesta de la IA no se pudo usar: %s", error)
        return None
    except httpx.HTTPError as error:
        # Ni la credencial ni el texto del documento entran al registro
        # (Art. X.2): solo la clase del error.
        registro.warning(
            "LiteLLM no respondió una propuesta utilizable (%s).",
            type(error).__name__,
        )
        return None
    except Exception as error:  # noqa: BLE001
        registro.warning(
            "Falla inesperada al pedir la propuesta (%s).", type(error).__name__
        )
        return None

    if propuesta is None:
        registro.info(
            "La propuesta quedó vacía tras descartar lo que no estaba en el documento."
        )
    return propuesta
