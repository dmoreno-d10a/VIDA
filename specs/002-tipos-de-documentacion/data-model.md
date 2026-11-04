# Modelo de datos: Tipos de documentación

**Spec:** [`spec.md`](./spec.md) · **Plan:** [`plan.md`](./plan.md) · **Investigación:** [`research.md`](./research.md)
**Rama:** `feature/002-tipos-de-documentacion`
**Fecha:** 2026-11-03

Dos tablas nuevas. Nada de lo que viene abajo cambia las tablas de la 001 (`usuario`, `sesion`).

---

## Panorama

```mermaid
erDiagram
    TIPO_DOCUMENTACION ||--o{ FORMATO_VERSION : "tiene versiones"
    TIPO_DOCUMENTACION }o--|| FORMATO_VERSION : "apunta a la vigente"

    TIPO_DOCUMENTACION {
        int id PK
        string nombre UK
        string descripcion
        bool desactivado
        int version_vigente_id FK
        datetime creado_en
        datetime actualizado_en
    }

    FORMATO_VERSION {
        int id PK
        int tipo_id FK
        int numero
        string nombre_archivo_original
        string extension
        int tamano_bytes
        string hash_sha256
        string ruta_almacenada
        jsonb estructura
        string origen
        datetime confirmada_en
        datetime creado_en
    }
```

La doble relación es intencional: una versión pertenece a un tipo, y el tipo señala **cuál** de
sus versiones es la vigente. Esa referencia es lo que hace imposible que dos versiones se
declaren vigentes a la vez (decisión 7 de `research.md`).

## `tipo_documentacion`

| Columna | Tipo | Reglas | Requerimiento |
|---|---|---|---|
| `id` | `INTEGER` | Clave primaria | — |
| `nombre` | `VARCHAR(200)` | Obligatorio, **único**, no vacío tras quitar espacios | RF-02 |
| `descripcion` | `VARCHAR(1000)` | Puede faltar | RF-02 |
| `desactivado` | `BOOLEAN` | Obligatorio, por defecto `false` | RF-14 |
| `version_vigente_id` | `INTEGER` | Puede faltar → el tipo está **incompleto**. FK a `formato_version.id` | RF-19 |
| `creado_en` | `TIMESTAMPTZ` | `now()` del servidor | — |
| `actualizado_en` | `TIMESTAMPTZ` | `now()` del servidor, se actualiza al modificar | — |

### El estado no se guarda: se deriva

RF-03 pide distinguir tres estados. Se calculan, no se almacenan:

| Estado | Condición | Lo ve el RO |
|---|---|---|
| `incompleto` | `version_vigente_id IS NULL` —incluye el tipo con una propuesta de la IA sin confirmar | No (RF-16) |
| `activo` | `version_vigente_id IS NOT NULL` y `desactivado = false` | Sí |
| `desactivado` | `desactivado = true` | No (RF-16) |

**Por qué derivado y no una columna `estado`.** Con una columna existiría el estado imposible
«activo sin formato vigente», y habría que mantener dos datos sincronizados que dicen lo mismo.
Derivarlo hace que ese estado no pueda escribirse. `desactivado` sí se guarda, porque es una
decisión del Administrador y no se deduce de nada.

Un tipo desactivado que nunca tuvo formato sigue mostrándose como `desactivado`: la tabla está en
orden de precedencia.

### Unicidad del nombre

El índice único va sobre `lower(trim(nombre))`, no sobre `nombre`. Si no, «Adapter Reverso» y
«adapter reverso» convivirían, y para el Administrador son el mismo tipo. El nombre se **guarda
tal como lo escribió** (Art. II: no se normaliza el dato del usuario); lo que se normaliza es la
comparación.

## `formato_version`

| Columna | Tipo | Reglas | Requerimiento |
|---|---|---|---|
| `id` | `INTEGER` | Clave primaria | — |
| `tipo_id` | `INTEGER` | Obligatorio, FK a `tipo_documentacion.id`, `ON DELETE CASCADE` | RF-19 |
| `numero` | `INTEGER` | Obligatorio, empieza en 1, **único por tipo** | RF-21 |
| `nombre_archivo_original` | `VARCHAR(255)` | Obligatorio, tal como lo trajo el archivo | RF-20 |
| `extension` | `VARCHAR(5)` | `docx` o `xlsx` | RF-04 |
| `tamano_bytes` | `INTEGER` | Obligatorio | RF-18 |
| `hash_sha256` | `CHAR(64)` | Obligatorio | RF-20 |
| `ruta_almacenada` | `VARCHAR(500)` | Obligatorio, **relativa** a `VIDA_ALMACEN_FORMATOS` | RF-09, RF-20 |
| `estructura` | `JSONB` | Obligatoria | RF-05, RF-06, RF-20 |
| `origen` | `VARCHAR(20)` | Obligatorio: `lectura` o `propuesta_ia` | RF-05c, RF-20 |
| `confirmada_en` | `TIMESTAMPTZ` | Puede faltar solo si `origen = propuesta_ia` y nadie la ha confirmado | RF-08a, RF-20 |
| `creado_en` | `TIMESTAMPTZ` | `now()` del servidor. Es el «desde cuándo» del historial | RF-21 |

**`ruta_almacenada` es relativa** a la carpeta configurada, no absoluta. Una ruta absoluta
guardada en la base rompe el sistema en cuanto se mueve el almacén, se despliega en otra máquina
o se trabaja en un worktree con otra configuración.

### `origen` y `confirmada_en`: qué puede quedar vigente

`origen` dice de dónde salió la estructura, y es lo que hace rastreable la diferencia entre lo
que el archivo trae marcado y lo que la IA propuso (RF-20).

| `origen` | `confirmada_en` | Puede ser la versión vigente |
|---|---|---|
| `lectura` | la misma fecha de creación | **Sí**, de inmediato: no hay nada que haya podido inventarse |
| `propuesta_ia` | vacío | **No.** El tipo sigue incompleto (RF-08a) |
| `propuesta_ia` | con fecha | **Sí**, desde que el Administrador la confirmó |

**La regla, dicha de una vez:** `tipo_documentacion.version_vigente_id` solo puede apuntar a una
versión con `confirmada_en` definida. Es la única forma en que el criterio CE-11 —ningún tipo
activo con estructura sin confirmar— deja de depender de que el código recuerde revisarlo.

`confirmada_en` se escribe **una sola vez**. Confirmar no es un interruptor: una estructura
confirmada no se «desconfirma», porque la versión es inmutable. Si el Administrador se equivocó,
corrige el archivo y carga una versión nueva, igual que para cualquier otra corrección.

**No se guarda quién confirmó.** La spec deja el registro de auditoría de usuarios fuera de
alcance (sección 8); lo que el Art. IX necesita es saber que la estructura fue revisada y cuándo,
no por quién.

**Las versiones no se borran ni se editan.** Solo se insertan. Es lo que sostiene el Art. IX:
una versión es el registro de qué estructura estaba vigente en un momento, y reescribirla
borraría la trazabilidad del documento que se generó con ella.

## La estructura reconocida (`estructura`)

Un documento JSON con una forma por cada clase de formato. Las listas están **en el orden del
archivo**, y ese orden es el dato (Art. I).

### Word

```json
{
  "clase": "word",
  "secciones": [
    { "nombre": "Contexto del servicio", "nivel": 1 },
    { "nombre": "Request",               "nivel": 2 },
    { "nombre": null,                    "nivel": 2 }
  ]
}
```

`"nombre": null` es un título sin texto en el archivo. Se registra como viene y **no** se le
inventa un nombre (RF-11). La posición en la lista lo identifica.

### Excel

```json
{
  "clase": "excel",
  "hojas": [
    {
      "nombre": "Request",
      "fila_de_encabezados": 3,
      "columnas": ["Campo", "Tipo", "Obligatorio", "Campo"]
    },
    { "nombre": "Response", "fila_de_encabezados": 1, "columnas": [] }
  ]
}
```

- `fila_de_encabezados` deja a la vista qué fila se tomó, para que el Administrador lo confirme
  (RF-08) y la decisión no quede escondida.
- `"Campo"` aparece dos veces porque así viene en el archivo: las columnas de nombre repetido se
  conservan todas, sin fusionarlas ni renumerarlas (sección 7 de la spec).
- `columnas: []` es una hoja sin encabezados. Es válida; lo que no es válido es un formato del
  que no se reconozca **nada** (ver abajo).

### La regla de «sin estructura reconocible»

Tras la lectura directa, la estructura está vacía cuando:

- Word: `secciones` vacía.
- Excel: ninguna hoja con al menos una columna.

Un Excel con hojas pero sin un solo encabezado no sirve para generar nada, así que cuenta como
sin estructura.

Eso ya **no es el rechazo**: es la condición que dispara el respaldo con IA (RF-05c). El rechazo
de RF-10 llega cuando, además, la propuesta de la IA queda vacía tras el descarte de RF-05d, o
el respaldo está apagado, o no responde.

### La estructura que propone la IA

Tiene la **misma forma** que la leída del archivo: el `JSONB` no cambia según el origen, y eso es
a propósito. Las funcionalidades 004, 005 y 006 consumen la estructura sin tener que saber de
dónde salió; lo que necesite distinguirlo lee `origen`.

En Word, una propuesta trae `nivel` como cualquier sección: la jerarquía es parte de lo que se
le pide. Lo que la propuesta **no** puede traer es un `nombre` que no aparezca literalmente en el
texto extraído del documento. El descarte ocurre antes de guardar, así que en la base de datos
no queda registro de lo descartado: lo que no entró, no existió.

## Estados y transiciones de un tipo

```mermaid
stateDiagram-v2
    [*] --> incompleto: crear (RF-01)
    incompleto --> activo: cargar formato válido (RF-19)
    incompleto --> [*]: eliminar (RF-15)
    activo --> activo: reemplazar formato — versión nueva (RF-13)
    activo --> desactivado: desactivar (RF-14)
    desactivado --> activo: reactivar (RF-14)
    incompleto --> incompleto: carga rechazada — el tipo no cambia (RF-10)
```

Lo que **no** existe como transición: volver a `incompleto` desde `activo`. Una vez que un tipo
tiene una versión vigente, no se le puede quitar. Para sacarlo de circulación está desactivarlo.

**Eliminar** solo se permite en `incompleto`, que es la lectura literal de RF-15 («tipos que
nunca han sido usados»): un tipo sin formato vigente nunca pudo ser elegido por un RO. El
`ON DELETE CASCADE` cubre el caso de un tipo con versiones rechazadas; si llegara a tener
versiones, se van con él.

> Cuando la 003 introduzca la actividad, «en uso» pasará a significar «tiene actividades». Esta
> funcionalidad no conoce la actividad y no se adelanta a definirla.

## Migración

Una sola migración de Alembic, con las dos tablas y la clave foránea cruzada.

**El orden importa:** `tipo_documentacion.version_vigente_id` apunta a `formato_version`, y
`formato_version.tipo_id` apunta de vuelta. Se crean las dos tablas y la segunda FK se agrega
después con `ALTER TABLE`, o se declara como `use_alter=True`. Declararlas juntas en el `CREATE`
falla porque cada tabla necesita que la otra exista.

`version_vigente_id` lleva `ON DELETE SET NULL` y `use_alter=True`; `tipo_id` lleva
`ON DELETE CASCADE`.

> **Convención de trabajo en paralelo:** si la 007 entra a `main` antes que esta rama, hay que
> regenerar esta migración sobre la cabeza nueva. Quien mezcla segundo regenera
> ([`CONTRIBUTING.md`](../../CONTRIBUTING.md#trabajo-en-paralelo)).
