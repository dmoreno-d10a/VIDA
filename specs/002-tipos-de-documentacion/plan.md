# Plan técnico: Tipos de documentación

**Spec:** [`spec.md`](./spec.md)
**Rama:** `feature/002-tipos-de-documentacion`
**Fecha:** 2026-11-03

> El plan describe **cómo** se va a cumplir la spec. Cada decisión debe poder rastrearse a un
> requerimiento (RF-XX) o historia (HU-X).

**Artefactos de diseño:** [`research.md`](./research.md) · [`data-model.md`](./data-model.md) ·
[`contracts/api-tipos-de-documentacion.md`](./contracts/api-tipos-de-documentacion.md) ·
[`quickstart.md`](./quickstart.md)

---

## 1. Resumen del enfoque

Se agregan dos tablas (`tipo_documentacion` y `formato_version`), un enrutador de administración
y uno de consulta para los RO en el backend, y dos pantallas en el front. Todo sigue las
convenciones que dejó la 001: la lógica y las credenciales viven en el backend (Art. IV), la
autorización se resuelve con la dependencia `exigir_administrador` aplicada al enrutador
completo, y el front llama al backend únicamente por `frontend/lib/api.ts`.

El corazón de la funcionalidad es el **reconocimiento del formato**, y se resuelve en dos pasos
con prioridades distintas. El principal es **determinista**: la estructura de un `.docx` se lee
con `python-docx` y la de un `.xlsx` con `openpyxl`, recorriendo párrafos y hojas. Lo que sale de
ahí está en el archivo o no sale, y por eso manda.

El segundo es el **respaldo con IA** (RF-05c), para el formato que un lector no puede reconocer
porque marca sus secciones con negrita o con tamaño de letra en vez de estilos de título. Solo
corre cuando la lectura directa no reconoció **nada**, y lleva dos cercos: se le manda el texto
extraído y nunca el archivo (Art. VI), y se descarta todo nombre que no aparezca literalmente en
el documento (RF-05d). Esto hace que la 002 **sí llegue a LiteLLM y VORKAN**, por una sola puerta
y apagable por configuración (decisiones 1 y 11 de `research.md`).

**Para qué sirve la estructura reconocida, dicho sin rodeos:** es la lista de **qué hay que
llenar**, que es lo que la 004 necesita para saber qué preguntarle al RO. El documento final no
se reconstruye a partir de ella: se escribe **dentro del archivo original** (RF-09), y por eso el
estilo del formato se conserva sin que haga falta nada para protegerlo. Eso es lo que justifica
que el reconocimiento sea tan liviano como sea posible: una lista incompleta se nota en la 004 y
se arregla recargando el archivo, no corrompe un documento entregado.

La segunda decisión que organiza el diseño es el **versionado del formato** (RF-19 a RF-21),
resuelto como aclaración el 2026-11-03. Cada carga produce una versión inmutable con su archivo
y su estructura; el tipo apunta a cuál es la vigente. Eso es lo que permite que un documento
generado el mes pasado se siga explicando contra el formato que lo produjo, que es lo que exige
el Art. IX.

## 2. Contexto técnico

| Aspecto | Decisión | Incógnitas |
|---|---|---|
| Lenguaje y versión | Python ≥ 3.12 (backend), TypeScript con Next.js (front), tal como la 001 | — |
| Dependencias nuevas | `python-docx>=1.1`, `openpyxl>=3.1` y `httpx>=0.28` —que ya estaba como dependencia de pruebas— para hablar con LiteLLM por HTTP. No entra `pandas`, ni `markitdown`, ni un SDK de proveedor | — |
| Almacenamiento | PostgreSQL para los datos y la estructura reconocida (`JSONB`); sistema de archivos para el archivo original, en carpeta configurable | — |
| Pruebas | `pytest` en el backend, Playwright en el front. Los cuatro formatos de prueba se generan con datos ficticios | — |
| Tiempo de respuesta | Techo de **30 s** para la carga completa, medido **punta a punta** y con la consulta a la IA incluida. **Síncrona** en la misma petición, sin procesamiento en segundo plano (aclaraciones del 2026-11-04) | — |
| Modelos / proveedor | LiteLLM hacia VORKAN, **solo en el paso de respaldo**. Dirección, credencial y nombre de la tarea por variable de entorno: ningún modelo queda escrito en el código (Art. V). Se puede apagar con `VIDA_IA_RESPALDO=0` | — |

No quedan incógnitas abiertas: las diez que había se resolvieron en la Fase 0, y la once
—cómo entra la IA— se resolvió al revisar la decisión 1 el 2026-11-04.

## 3. Verificación contra la constitución

| Artículo | ¿Cumple? | Cómo |
|---|---|---|
| I — El formato definido manda | Sí | Una sección es un párrafo con estilo de título y nada más; los encabezados de una hoja salen de su primera fila con contenido (RF-05a, RF-05b). La estructura se lee de forma determinista y se guarda como listas ordenadas en `JSONB`, sin normalizar nada. Las secciones y columnas de nombre repetido se conservan todas; las sin nombre se guardan como `null` sin inventarles uno. La prueba de reconocimiento compara contra la estructura exacta del archivo generado, así que el cumplimiento es verificable y no una opinión |
| II — Cero información inventada | Sí | La lectura principal no puede inventar: recorre el archivo. El respaldo con IA sí podría, y por eso cada nombre propuesto se busca literalmente en el texto del documento y se descarta si no está (RF-05d). Lo que la estructura decide es qué se le pregunta al RO, no qué dice el documento: el contenido lo pone el RO y el estilo lo pone el archivo original, que se llena en sitio. Un formato del que ni la lectura ni la IA reconocen nada se rechaza (RF-10) |
| III — El RO decide | N.A. | Esta funcionalidad no le pide información al RO: solo le ofrece la lista de tipos activos |
| IV — Separación de capas | Sí | Toda la lectura de archivos, la validación y la autorización están en el backend. El front no tiene credenciales ni decide permisos: oculta opciones por comodidad, y la barrera es la dependencia del enrutador |
| V — Independencia del modelo | Sí | El respaldo habla con LiteLLM por HTTP, no con un SDK de proveedor. Dirección, credencial y nombre de la tarea son variables de entorno; cambiar de modelo no toca código. El cliente está en un solo archivo, `propuesta_ia.py`, que es el único punto de la 002 que sale a la red |
| VI — Eficiencia de tokens | Sí | Ningún archivo se envía a un modelo: el respaldo manda el texto de los párrafos con sus señales de forma, o los nombres de las hojas con sus primeras filas, que es el esqueleto y no el contenido. Y solo cuando la lectura directa no reconoció nada: el formato que trae estilos de título no cuesta un token. El formato se analiza **una sola vez** al cargarlo y la estructura se lee después de la base de datos: reabrir el detalle no reprocesa nada (RF-07) |
| VII — Constructor / Evaluador | N.A. | No se genera ningún documento aquí, así que no hay nada que evaluar. Aplica desde la 005 |
| VIII — Generalización | Sí | Ningún nombre de sección queda escrito en el código: la plataforma reconoce lo que traiga el archivo (RF-17). Se valida con tres formatos, dos de ellos ajenos al caso de referencia, uno Word y uno Excel |
| IX — Trazabilidad | Sí | El versionado es lo que lo sostiene: cada versión guarda su archivo, su hash y su estructura, y no se edita ni se borra nunca. Las funcionalidades posteriores pueden atar un documento a la versión con la que se produjo (RF-20) |
| X — Seguridad y datos | Sí | Solo el Administrador administra tipos, por dependencia del enrutador. Los archivos se guardan bajo `uploads/`, ya excluido en `.gitignore`. La credencial de LiteLLM se lee del entorno y no tiene valor por defecto ni aparece en `.env.ejemplo` con contenido (X.2). Los tres formatos de prueba son ficticios y **generados**: el formato real del cliente no entra al repositorio (X.3) |
| XI — Spec antes que código | Sí | Este plan sale de una spec aprobada y sin aclaraciones abiertas. No se escribe código antes de `tasks.md` |
| XII — Idioma | Sí | Código, mensajes de error, pantallas y estos artefactos, en español |

**X.4 y X.5 siguen pendientes en la constitución.** El X.4 —retención y eliminación de los
archivos cargados— ahora también alcanza a las versiones anteriores de un formato, que esta
funcionalidad conserva indefinidamente a propósito. No bloquea la implementación, pero conviene
resolverlo antes de que la plataforma acumule formatos de verdad, y se resuelve enmendando la
constitución, no aquí.

Esta tabla se vuelve a revisar al cerrar la Fase 1. **Revisada el 2026-11-04:** el respaldo con
IA movió el Art. V de «no aplica» a «sí», y cambió el argumento del Art. II, que ya no se apoya
en que no haya modelo sino en los tres cercos de la decisión 11. Ninguna otra fila cambió.

## 4. Componentes

| Componente | Tipo | Responsabilidad | RF / HU que cubre |
|---|---|---|---|
| `backend/app/modelos/tipo_documentacion.py` | Modelo | `TipoDocumentacion` y `FormatoVersion`, con el estado derivado | RF-02, RF-03, RF-19 |
| `backend/app/esquemas/tipos_de_documentacion.py` | Esquemas | Entradas y salidas de la API, con las validaciones de nombre | RF-02, RF-12 |
| `backend/app/formatos/lector_word.py` | Lógica | Lee las secciones de un `.docx` con su nivel y su orden | RF-05, RF-06, RF-11 |
| `backend/app/formatos/lector_excel.py` | Lógica | Lee hojas, fila de encabezados y columnas de un `.xlsx` | RF-05, RF-06, RF-11 |
| `backend/app/formatos/reconocimiento.py` | Lógica | Puerta única: valida tamaño, extensión y firma, elige el lector, y si no reconoce nada llama al respaldo | RF-04, RF-05c, RF-10, RF-18 |
| `backend/app/formatos/texto_para_ia.py` | Lógica | Extrae el esqueleto que se le manda a la IA: párrafos con sus señales de forma, u hojas con sus primeras filas. Nunca el archivo | Art. VI |
| `backend/app/formatos/propuesta_ia.py` | Lógica | Único punto que sale a la red: pide la propuesta a LiteLLM y **descarta** todo nombre que no aparezca literalmente en el texto | RF-05c, RF-05d, Art. V |
| `backend/app/formatos/almacen.py` | Lógica | Escribe y lee el archivo en la carpeta configurada, calcula el hash y encapsula la ruta | RF-09, RF-20 |
| `backend/app/rutas/tipos_de_documentacion.py` | Rutas | Administración de tipos y carga de formatos. Exige Administrador en el enrutador | RF-01, RF-12 a RF-15, RF-21 |
| `backend/app/rutas/tipos_disponibles.py` | Rutas | Lista de tipos activos para los RO. Solo exige sesión | RF-16 |
| `backend/app/configuracion.py` | Config | Tres parámetros del almacén y la carga, más cuatro del respaldo: interruptor, dirección de LiteLLM, credencial y nombre de la tarea | RF-18, Art. V |
| `backend/alembic/versions/*_tipos_de_documentacion.py` | Migración | Las dos tablas y la clave foránea cruzada | RF-02, RF-19 |
| `backend/scripts/generar_formatos_de_prueba.py` | Script | Genera los cuatro formatos ficticios y la estructura esperada de cada uno | Art. VIII, Art. X.3 |
| `frontend/app/(privado)/administracion/tipos-de-documentacion/` | Pantallas | Listado y detalle con la estructura y el historial | HU-1 a HU-4 |
| `frontend/lib/api.ts` | Cliente | Se extiende para aceptar `FormData` en la carga del archivo | HU-2 |
| `frontend/app/componentes/menu-por-rol.tsx` | Componente | La opción nueva en el menú del Administrador | HU-1 |

**Por qué `app/formatos/` es un paquete aparte** y no vive dentro de las rutas: el reconocimiento
es la única parte de esta funcionalidad que las siguientes van a reutilizar —la 004 y la 005
trabajan sobre la estructura, y la 006 sobre el archivo—. Separarlo también hace que se pueda
probar sin levantar la API.

## 5. Flujo

La carga de un formato, que es donde está todo lo que importa:

```mermaid
flowchart TD
  A[Administrador carga el archivo] --> B{¿Tamaño dentro del límite?}
  B -- No --> R1[413: rechaza mientras recibe]
  B -- Sí --> C{¿Extensión .docx o .xlsx?}
  C -- No --> R2[415: indica las admitidas]
  C -- Sí --> D{¿Firma ZIP del archivo?}
  D -- No --> R2
  D -- Sí --> E[Calcula SHA-256 y guarda en el almacén]
  E --> F{¿Qué clase es?}
  F -- Word --> G[lector_word: secciones con nivel y orden]
  F -- Excel --> H[lector_excel: hojas, fila de encabezados y columnas]
  G --> I{¿Se reconoció alguna estructura?}
  H --> I
  I -- Error al abrir --> R4[422: dañado o protegido]
  I -- Sí --> J[Transacción: candado del tipo]
  I -- No --> N{¿Respaldo con IA encendido?}
  N -- No --> R3[422: dice qué se esperaba encontrar]
  N -- Sí --> O[texto_para_ia: párrafos u hojas, nunca el archivo]
  O --> P[LiteLLM propone la estructura]
  P -- No responde --> R3
  P --> Q[Descarta todo nombre que no esté literalmente en el texto]
  Q --> S{¿Quedó algo?}
  S -- No --> R3
  S -- Sí --> J
  J --> K[Inserta la versión y apunta el tipo a ella]
  K --> L[201: queda vigente, el tipo pasa a activo]

  R1 --> M[El tipo queda como estaba]
  R2 --> M
  R3 --> M
  R4 --> M
```

En los cuatro rechazos el tipo conserva su versión vigente, o sigue incompleto (RF-10). El
archivo se escribe **antes** de abrir la transacción, para que dentro de ella no haya entrada ni
salida de disco —ni, ahora, una llamada a la red—; si la transacción falla, sobra un archivo que
nadie referencia, que es el lado correcto en el que fallar.

La llamada a la IA queda **fuera de la transacción** por la misma razón, y con más fuerza: una
transacción abierta mientras se espera una respuesta de la red sostiene el candado del tipo
durante segundos. Primero se resuelve la propuesta, después se abre la transacción.

**El final no se bifurca:** la versión queda vigente venga su estructura de la lectura o de la
propuesta. La revisión del Administrador ocurre después, en la pantalla de detalle (RF-08), y lo
que hace si la estructura no corresponde es corregir el archivo y recargarlo.

## 6. Configuración

| Parámetro | Valor por defecto | Dónde se define |
|---|---|---|
| `VIDA_ALMACEN_FORMATOS` | `uploads/formatos` | Variable de entorno, relativa a la raíz del repositorio |
| `VIDA_FORMATO_MB_MAX` | `25` | Variable de entorno (RF-18) |
| `VIDA_FORMATO_EXTENSIONES` | `docx,xlsx` | Variable de entorno (RF-18) |
| `VIDA_IA_RESPALDO` | `1` | Interruptor del respaldo. En `0`, un formato sin estructura se rechaza como en el diseño original |
| `VIDA_LITELLM_URL` | `http://localhost:4000` | Dirección de LiteLLM hacia VORKAN |
| `VIDA_LITELLM_API_KEY` | **sin valor** | Credencial. No tiene valor por defecto y en `.env.ejemplo` va vacía (Art. X.2) |
| `VIDA_MODELO_RECONOCIMIENTO` | `reconocimiento-de-formato` | Nombre de la tarea en LiteLLM, no un modelo concreto (Art. V) |

Todas tienen valor por defecto salvo la credencial, así que un `.env` de la 001 sigue
funcionando sin tocarlo: lo que pasa sin credencial es que el respaldo no está disponible y la
carga se comporta como si estuviera apagado. Las siete se agregan a `.env.ejemplo`, que es uno
de los archivos que todas las ramas tocan.

**`VIDA_MODELO_RECONOCIMIENTO` nombra una tarea, no un modelo.** Qué modelo atiende esa tarea lo
resuelve LiteLLM, y elegirlo es de la funcionalidad 007. Escribir aquí el nombre de un modelo
concreto sería justo lo que el Art. V prohíbe.

## 7. Estructura de archivos que se crean o modifican

```
backend/
├── app/
│   ├── configuracion.py                      # MODIFICA: tres parámetros nuevos
│   ├── main.py                               # MODIFICA: registra los dos enrutadores
│   ├── formatos/                             # NUEVO paquete
│   │   ├── __init__.py
│   │   ├── reconocimiento.py                 # puerta única: valida y despacha
│   │   ├── lector_word.py
│   │   ├── lector_excel.py
│   │   ├── texto_para_ia.py                  # el esqueleto que se le manda, no el archivo
│   │   ├── propuesta_ia.py                   # LiteLLM y el descarte de lo inventado
│   │   └── almacen.py                        # archivo en disco, hash y ruta
│   ├── modelos/
│   │   ├── __init__.py                       # MODIFICA: importa los modelos nuevos
│   │   └── tipo_documentacion.py             # NUEVO
│   ├── esquemas/
│   │   └── tipos_de_documentacion.py         # NUEVO
│   └── rutas/
│       ├── tipos_de_documentacion.py         # NUEVO: administración
│       └── tipos_disponibles.py              # NUEVO: consulta de los RO
├── alembic/versions/
│   └── xxxx_tipos_de_documentacion.py        # NUEVO
├── scripts/
│   └── generar_formatos_de_prueba.py         # NUEVO
├── tests/
│   ├── test_tipos_de_documentacion.py        # NUEVO
│   ├── test_reconocimiento_de_formato.py     # NUEVO
│   ├── test_respaldo_con_ia.py               # NUEVO
│   └── test_versiones_de_formato.py          # NUEVO
└── pyproject.toml                            # MODIFICA: python-docx, openpyxl, httpx

frontend/
├── app/(privado)/administracion/tipos-de-documentacion/
│   ├── page.tsx                              # NUEVO: listado
│   └── [id]/page.tsx                         # NUEVO: detalle, estructura e historial
├── app/componentes/menu-por-rol.tsx          # MODIFICA: la opción nueva
├── lib/api.ts                                # MODIFICA: acepta FormData
└── e2e/tipos-de-documentacion.spec.ts        # NUEVO

.env.ejemplo                                  # MODIFICA: las siete variables
.specify/memory/mapa-funcionalidades.md       # MODIFICA: estado de la 002 al cerrar
```

## 8. Estrategia de validación

- **Caso de referencia:** Word con la estructura del Adapter Reverso y contenido ficticio.
- **Casos de generalización:** un Word de otra forma (jerarquía distinta, títulos repetidos, uno
  sin nombre) y un Excel (varias hojas, encabezados fuera de la fila 1, columnas repetidas).
- **Caso del respaldo:** un cuarto Word ficticio que marca sus secciones **con negrita**, sin
  ningún estilo de título. Es el que ejercita RF-05c de punta a punta.
- **Qué se compara:** la estructura reconocida contra la que el script generador sabe que
  escribió —nombres, cantidad, orden y nivel—; los cuatro rechazos con su código y su mensaje; y
  que el tipo quede intacto tras cada rechazo.
- **Cómo se prueba el respaldo sin llamar a VORKAN:** las pruebas sustituyen el cliente de
  LiteLLM por uno que devuelve una respuesta fija, y verifican las dos cosas que importan: que un
  nombre que **no** está en el documento se descarte (RF-05d), y que la lectura directa tenga
  prioridad cuando el archivo sí trae estilos. Ninguna prueba del repositorio sale a la red.

Los tres archivos se **generan**, no se cometen: el formato real de un cliente no puede entrar al
repositorio (Art. X.3), y generar deja la estructura esperada escrita al lado del código que
produce el archivo, en vez de contra un valor mágico.

El recorrido manual completo, historia por historia, está en [`quickstart.md`](./quickstart.md).

## 9. Migraciones de base de datos

Una sola migración, con las dos tablas. La clave foránea de `tipo_documentacion.version_vigente_id`
hacia `formato_version` es cruzada —cada tabla referencia a la otra— así que se declara con
`use_alter=True` para que Alembic la agregue con un `ALTER TABLE` después de crear las dos tablas.

> **Convención de trabajo en paralelo:** la 007 es la otra funcionalidad que puede avanzar hoy, y
> también va a generar migración. **Quien mezcla segundo regenera la suya** sobre la cabeza nueva
> ([`CONTRIBUTING.md`](../../CONTRIBUTING.md#trabajo-en-paralelo)). Esta migración no toca las
> tablas de la 001, así que el único conflicto esperable es el de las dos cabezas.

## 10. Riesgos y decisiones abiertas

| Riesgo / decisión | Impacto | Mitigación |
|---|---|---|
| Un Word del área marca sus secciones con negrita o tamaño de letra, no con estilos de título | Era el riesgo que podía invalidar la funcionalidad | **Resuelto por la aclaración del 2026-11-04:** ese es ahora el caso del respaldo con IA (RF-05c), no un rechazo. Sigue valiendo la pena saber qué usa el área (T001), pero ya no para decidir si la funcionalidad sirve, sino para saber **cuál de los dos caminos** va a ser el habitual y cuánto va a costar |
| La IA propone una estructura plausible que el documento no tiene —los nombres están, pero no eran secciones— | La 004 le preguntaría al RO por una sección que su formato no tiene, o dejaría de preguntarle por una que sí | El descarte de RF-05d quita los nombres que no están en el texto, que es lo verificable mecánicamente. El resto se ve en la pantalla de detalle (RF-08) y, cuando la 004 exista, al abrir una actividad: el síntoma es visible y la corrección es recargar el archivo. Lo que **no** está en riesgo es el documento entregado, porque se escribe dentro del archivo original |
| El respaldo con IA no responde, responde tarde o VORKAN no está disponible | La carga de un formato sin estilos de título fallaría, y con el techo de 30 s de por medio | El respaldo tiene un tiempo límite propio, menor que el techo de la carga, y al agotarse la carga se rechaza con el mensaje de RF-10: nunca queda a medias. `VIDA_IA_RESPALDO=0` permite operar sin VORKAN, con el comportamiento del diseño original |
| La base y el disco se desincronizan: la versión existe y el archivo no | La 006 no podría generar el documento de ese tipo | El hash permite detectarlo. La ruta está encapsulada en `almacen.py`, así que pasar a `BYTEA` más adelante es un cambio local (decisión 6 de `research.md`) |
| Versiones que se acumulan sin límite | Crecimiento del disco con archivos que nadie consulta | Es deliberado: el Art. IX lo exige. La limpieza depende del pendiente X.4 de la constitución |
| Un `.xlsx` de 25 MB con muchas hojas, o un `.docx` grande que además necesite el respaldo, se acerca al techo de 30 s | La carga se sentiría lenta, y pasar de 30 s incumpliría un criterio medible | `openpyxl` en modo solo lectura y el análisis una sola vez acotan el costo. La aclaración del 2026-11-04 cerró la arquitectura: **síncrona siempre**, sin proceso en segundo plano. Una tarea de la fase de validación mide el caso de 25 MB contra el techo, de modo que si no alcanza se sepa antes de cerrar la funcionalidad y no en producción |
| `pedirApi` hoy serializa a JSON siempre | La carga del archivo no funcionaría | Se extiende para aceptar `FormData` y, en ese caso, no fijar `Content-Type`: el navegador debe poner el suyo con el delimitador. Es aditivo y no altera las llamadas existentes |
