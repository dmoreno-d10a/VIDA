# Contrato de la API: Tipos de documentación

**Spec:** [`../spec.md`](../spec.md) · **Plan:** [`../plan.md`](../plan.md) · **Modelo:** [`../data-model.md`](../data-model.md)
**Rama:** `feature/002-tipos-de-documentacion`
**Fecha:** 2026-11-03

Dos enrutadores nuevos. Todas las rutas exigen sesión; las de administración exigen además el
rol Administrador, por la dependencia del enrutador completo, como en la 001.

**Convenciones heredadas de la 001**, que este contrato respeta:

- El error va siempre en la clave `detalle`, en español (`main.py`).
- La sesión viaja en la cookie que define `app/seguridad/sesiones.py`. No hay tokens en cabeceras.
- Negar por rol responde `403` con un mensaje que no describe la opción pedida (RF-05 de la 001).

---

## Enrutador de administración — `/tipos-de-documentacion`

`dependencies=[Depends(exigir_administrador)]`, una sola vez para todo el archivo.

| Método | Ruta | Qué hace | RF |
|---|---|---|---|
| `GET` | `/tipos-de-documentacion` | Lista todos los tipos con su estado | RF-03 |
| `POST` | `/tipos-de-documentacion` | Crea un tipo | RF-01, RF-02 |
| `GET` | `/tipos-de-documentacion/{id}` | Detalle: datos, estructura vigente e historial | RF-08, RF-21 |
| `PATCH` | `/tipos-de-documentacion/{id}` | Cambia nombre y descripción | RF-12 |
| `DELETE` | `/tipos-de-documentacion/{id}` | Elimina un tipo incompleto | RF-15 |
| `POST` | `/tipos-de-documentacion/{id}/formato` | Carga o reemplaza el formato → versión nueva | RF-04 a RF-11, RF-13, RF-19 |
| `GET` | `/tipos-de-documentacion/{id}/formato/versiones/{numero}` | Estructura de una versión anterior | RF-21 |
| `POST` | `/tipos-de-documentacion/{id}/activacion` | Desactiva o reactiva | RF-14 |

### `GET /tipos-de-documentacion`

`200` con la lista, ordenada por nombre:

```json
[
  {
    "id": 1,
    "nombre": "Adapter Reverso",
    "descripcion": "Documentación de adapters de reverso",
    "estado": "activo",
    "version_vigente": { "numero": 2, "extension": "docx", "creado_en": "2026-11-03T14:20:00Z" }
  },
  {
    "id": 2,
    "nombre": "Servicio nuevo",
    "descripcion": null,
    "estado": "incompleto",
    "version_vigente": null
  }
]
```

`estado` es `incompleto` | `activo` | `desactivado`, derivado como dice el modelo de datos.

### `POST /tipos-de-documentacion`

```json
{ "nombre": "Adapter Reverso", "descripcion": "Documentación de adapters de reverso" }
```

| Código | Cuándo | `detalle` |
|---|---|---|
| `201` | Creado | — (devuelve el tipo, con `estado: "incompleto"`) |
| `409` | El nombre ya existe, comparando sin mayúsculas ni espacios de sobra | `Ya existe un tipo de documentación con ese nombre.` |
| `422` | Falta el nombre o queda vacío al quitar espacios | Mensaje de validación de la 001 |

### `GET /tipos-de-documentacion/{id}`

`200` con el detalle. Es la pantalla que el Administrador usa para comparar lo reconocido con su
archivo (RF-08):

```json
{
  "id": 1,
  "nombre": "Adapter Reverso",
  "descripcion": "Documentación de adapters de reverso",
  "estado": "activo",
  "version_vigente": {
    "numero": 2,
    "nombre_archivo_original": "formato-adapter-reverso-v2.docx",
    "extension": "docx",
    "tamano_bytes": 48213,
    "creado_en": "2026-11-03T14:20:00Z",
    "estructura": {
      "clase": "word",
      "secciones": [
        { "nombre": "Contexto del servicio", "nivel": 1 },
        { "nombre": "Request", "nivel": 2 }
      ]
    }
  },
  "historial": [
    { "numero": 2, "nombre_archivo_original": "formato-adapter-reverso-v2.docx", "creado_en": "2026-11-03T14:20:00Z", "vigente": true },
    { "numero": 1, "nombre_archivo_original": "formato-adapter-reverso.docx",    "creado_en": "2026-10-28T09:05:00Z", "vigente": false }
  ]
}
```

- `historial` va de la versión más nueva a la más vieja, y marca la vigente (RF-21).
- La `estructura` de las versiones anteriores **no** viene aquí: se pide por su ruta, para que el
  detalle de un tipo con muchas versiones no crezca sin límite.
- `404` si el tipo no existe: `No existe ese tipo de documentación.`

### `POST /tipos-de-documentacion/{id}/formato`

`multipart/form-data` con un campo `archivo`. Es la ruta donde vive casi toda la funcionalidad.

`201` con la versión creada: `numero`, metadatos y `estructura` completa. La respuesta es la
misma esté la `estructura` llena o vacía, y en los dos casos la versión **queda vigente**: el
tipo pasa a activo.

| Código | Cuándo | `detalle` | RF |
|---|---|---|---|
| `201` | Aceptado, estructura reconocida, pasa a ser la vigente | — | RF-19 |
| `404` | El tipo no existe | `No existe ese tipo de documentación.` | — |
| `413` | Supera el tamaño máximo | `El archivo supera el tamaño máximo permitido (25 MB).` | RF-18 |
| `415` | Extensión no admitida, o la firma no corresponde a un archivo de Office actual | `Solo se admiten formatos de Word (.docx) y Excel (.xlsx).` | RF-04 |
| `422` | Dañado, protegido con contraseña o ilegible | `No se pudo leer el archivo. Puede estar dañado o protegido con contraseña.` | RF-10 |
| `409` | Otra carga sobre el mismo tipo está en curso | `Hay otra carga de formato en curso para este tipo. Intenta de nuevo en un momento.` | sección 7 |

**En todos los casos de error el tipo queda como estaba** (RF-10): conserva su versión vigente,
o sigue incompleto. El `413` se responde **mientras** se recibe el archivo, no después.

El mensaje del `415` nombra las extensiones admitidas, como pide RF-04. El del `422` por falta de
estructura dice qué se esperaba encontrar, porque es el error que el Administrador puede corregir
por sí mismo.

**No hay un `422` por «no se reconoció estructura».** Un formato que se pudo abrir se acepta
siempre, y la `estructura` viene vacía si no se reconoció nada (RF-05c, RF-10). El único `422`
es el del archivo que no se pudo abrir, y ese no es un juicio sobre su contenido: es que no hay
archivo con el que trabajar.

**No hay ruta para corregir una estructura reconocida.** Si no corresponde al archivo, el
Administrador corrige el archivo y lo vuelve a cargar, que produce una versión nueva. Editarla
aquí dejaría que la estructura guardada divergiera del archivo (sección 8 de la spec).

### `GET /tipos-de-documentacion/{id}/formato/versiones/{numero}`

`200` con la versión y su `estructura` completa. `404` si el tipo o esa versión no existen.
No vuelve a analizar el archivo: la estructura sale de la base de datos (RF-07).

### `PATCH /tipos-de-documentacion/{id}`

```json
{ "nombre": "Adapter de reverso", "descripcion": "Texto nuevo" }
```

Los dos campos son opcionales; se cambia lo que venga. `200` con el tipo actualizado.
**No toca la estructura reconocida** (RF-12). `409` si el nombre nuevo choca con otro tipo.

### `POST /tipos-de-documentacion/{id}/activacion`

```json
{ "desactivado": true }
```

`200` con el tipo y su estado nuevo. Es una ruta propia y no parte del `PATCH` porque es una
decisión distinta: corregir la descripción de un tipo y sacarlo de circulación no se piden en el
mismo gesto, y separarlas evita desactivar un tipo por accidente al renombrarlo.

| Código | Cuándo | `detalle` |
|---|---|---|
| `200` | Cambiado | — |
| `409` | Se intenta activar un tipo incompleto | `Este tipo no tiene un formato cargado, así que no puede activarse.` |

### `DELETE /tipos-de-documentacion/{id}`

| Código | Cuándo | `detalle` |
|---|---|---|
| `204` | Eliminado (estaba incompleto) | — |
| `409` | El tipo tiene una versión vigente | `Este tipo ya tiene un formato cargado y no se puede eliminar. Puedes desactivarlo para que los RO no lo vean.` |
| `404` | No existe | `No existe ese tipo de documentación.` |

El `409` **ofrece la alternativa** en el mismo mensaje, como pide RF-15.

---

## Enrutador para los RO — `/tipos-de-documentacion-disponibles`

Solo exige sesión, cualquier rol. Es lo único de esta funcionalidad que un RO alcanza.

### `GET /tipos-de-documentacion-disponibles`

`200` con los tipos activos, ordenados por nombre. Nada más que lo que el RO necesita para
elegir (RF-16):

```json
[ { "id": 1, "nombre": "Adapter Reverso", "descripcion": "Documentación de adapters de reverso" } ]
```

Devuelve `[]` cuando no hay ninguno; es el front el que convierte eso en el mensaje explícito que
pide HU-5, no una pantalla vacía.

**Por qué una ruta aparte y no un filtro en la de administración.** La ruta de administración
niega el paso a los RO desde el enrutador completo, de una sola vez. Si la misma ruta sirviera a
los dos roles con un filtro, la protección pasaría a depender de un `if` dentro de la función, y
ahí es donde se cometen los errores que la 001 decidió hacer imposibles. Este endpoint no expone
estructura, historial, versiones, tipos incompletos ni desactivados: ni filtrando ni pidiendo a
mano.

---

## Lo que el front consume

Todo a través de `pedirApi` / `pedirApiEnServidor` de [`frontend/lib/api.ts`](../../../frontend/lib/api.ts),
el único punto de llamada al backend (Art. IV). El front no decide permisos: oculta opciones por
comodidad, y la barrera está en el backend.

| Pantalla | Ruta del front | Endpoints |
|---|---|---|
| Listado de tipos | `/administracion/tipos-de-documentacion` | `GET`, `POST`, `DELETE`, `POST /activacion` |
| Detalle y estructura | `/administracion/tipos-de-documentacion/[id]` | `GET /{id}`, `PATCH`, `POST /{id}/formato`, `GET …/versiones/{numero}` |
| Tipos disponibles (RO) | `/inicio` o la pantalla que la 003 defina | `GET /tipos-de-documentacion-disponibles` |

La opción del menú se agrega en `frontend/app/componentes/menu-por-rol.tsx`, que es uno de los
archivos que todas las ramas tocan: al resolver el conflicto se conservan las dos partes
([`CONTRIBUTING.md`](../../../CONTRIBUTING.md#trabajo-en-paralelo)).

> La carga del archivo es el único lugar donde el front no usa JSON sino `multipart/form-data`.
> `pedirApi` hoy serializa a JSON siempre, así que hay que extenderlo para aceptar un `FormData`
> y, en ese caso, **no** fijar `Content-Type`: el navegador tiene que poner el suyo con el
> delimitador. Es un cambio aditivo y no altera las llamadas que ya existen.

> **La pantalla de detalle es donde el Administrador revisa la estructura** (RF-08), y es la única
> revisión que existe: ninguna ruta le exige confirmar nada antes de que el tipo quede activo. Si
> la estructura no corresponde, corrige el archivo y lo recarga.
