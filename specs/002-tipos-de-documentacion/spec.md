# Especificación: Tipos de documentación

**ID:** 002
**Rama:** `feature/002-tipos-de-documentacion`
**Autor:** Diego Moreno
**Fecha:** 2026-10-26
**Estado:** Borrador

> Una spec describe **qué** se necesita y **por qué**. No incluye tecnologías, librerías, estructura de código ni prompts. Eso va en `plan.md`.

---

## 1. Contexto y problema

Cada entrega que los Requirements Owners (RO) de VortexBird hacen a las fábricas de desarrollo tiene su propio formato: el documento de un adapter no se parece al de un servicio nuevo ni al de una migración, y cada cliente puede imponer el suyo. Hoy esos formatos viven como archivos sueltos de Word y Excel que cada RO copia de una entrega anterior. El resultado es que dos RO documentan la misma clase de trabajo con secciones distintas, y la fábrica recibe documentos que no puede leer de la misma manera.

V.I.D.A. no puede generar documentación sin saber antes **qué tipos de documentación existen** y **cómo es el formato de cada uno**. La funcionalidad 001 ya definió que esa configuración le corresponde al Administrador, pero todavía no existe dónde registrarla. Mientras no exista, no hay nada que el RO pueda elegir al abrir una actividad (funcionalidad 003), ni estructura contra la cual el sistema pueda detectar información faltante (004), ni plantilla que respetar al generar (005).

El Artículo I de la constitución dice que la estructura del documento la define el formato que cargó el Administrador, y que el sistema no agrega, quita, renombra ni reordena nada. Para que eso sea verificable, la estructura tiene que quedar **reconocida y guardada** en el momento de cargar el formato, no deducida cada vez que se genera un documento. El Artículo VI agrega la razón de eficiencia: el formato se analiza **una sola vez**, al cargarlo, y nunca se envía el archivo completo a un modelo en cada generación.

Esta funcionalidad existe para cerrar ese vacío: darle al Administrador el lugar donde declara los tipos de documentación de la plataforma, cargar el formato de cada uno y dejar su estructura reconocida y disponible para todo lo que viene después.

## 2. Usuarios

- **Administrador.** Único rol que crea, modifica, desactiva y elimina tipos de documentación, y el único que carga sus formatos. Es quien revisa que la estructura reconocida corresponda al formato que cargó.
- **RO (Requirements Owner).** No configura nada aquí: consume el resultado. En esta funcionalidad solo necesita **ver y elegir** los tipos de documentación activos, para poder abrir una actividad con uno de ellos (funcionalidad 003).
- **Funcionalidades posteriores de la plataforma.** La estructura reconocida es su insumo: el análisis de faltantes (004) y la generación del documento (005) trabajan sobre ella, no sobre el archivo original.
- **Fábrica de desarrollo.** No entra a la plataforma. Aparece aquí porque es quien recibe el documento final y la razón por la que su estructura debe conservarse tal como el formato la define.

## 3. Historias de usuario

### HU-1: Crear un tipo de documentación
**Como** Administrador, **quiero** registrar un tipo de documentación con su nombre y su descripción, **para** que los RO tengan una lista clara de qué clases de documento puede generar la plataforma.

**Criterios de aceptación:**
- **Dado** un Administrador autenticado, **cuando** crea un tipo indicando nombre y descripción, **entonces** el tipo queda registrado y aparece en el listado de tipos de documentación.
- **Dado** un Administrador, **cuando** intenta crear un tipo con un nombre que ya existe, **entonces** el sistema no lo crea y le indica el motivo.
- **Dado** un Administrador, **cuando** intenta crear un tipo sin nombre, **entonces** el sistema no lo crea y le indica qué dato falta.
- **Dado** un tipo recién creado al que todavía no se le ha cargado un formato, **cuando** el Administrador consulta el listado, **entonces** ve que ese tipo está **incompleto** y que aún no puede usarse.
- **Dado** un RO autenticado, **cuando** intenta abrir la administración de tipos de documentación, **entonces** el sistema se lo impide y no le muestra ninguna opción de creación ni de carga de formatos.

### HU-2: Cargar el formato de un tipo
**Como** Administrador, **quiero** cargar el archivo Word o Excel que define el formato de un tipo, **para** que los documentos que genere la plataforma salgan exactamente con esa estructura.

**Criterios de aceptación:**
- **Dado** un tipo de documentación registrado, **cuando** el Administrador carga un archivo Word válido como su formato, **entonces** el sistema lo acepta, reconoce su estructura y deja el tipo disponible para usarse.
- **Dado** un tipo de documentación registrado, **cuando** el Administrador carga un archivo Excel válido como su formato, **entonces** el sistema lo acepta, reconoce su estructura y deja el tipo disponible para usarse.
- **Dado** un Administrador, **cuando** intenta cargar un archivo que no es Word ni Excel, **entonces** el sistema lo rechaza, indica qué formatos admite y el tipo queda como estaba.
- **Dado** un Administrador, **cuando** carga un archivo dañado o que el sistema no logra interpretar, **entonces** el sistema lo rechaza, se lo informa y no deja el tipo en un estado a medias.
- **Dado** un archivo que supera el tamaño admitido, **cuando** el Administrador intenta cargarlo, **entonces** el sistema lo rechaza indicando el límite.

### HU-3: Confirmar la estructura reconocida
**Como** Administrador, **quiero** ver qué estructura reconoció el sistema en el formato que cargué, **para** confirmar que corresponde al documento real antes de que algún RO lo use.

**Criterios de aceptación:**
- **Dado** un formato Word cargado, **cuando** el Administrador abre el detalle del tipo, **entonces** ve las secciones reconocidas con sus nombres y en el mismo orden en que aparecen en el archivo.
- **Dado** un formato Excel cargado, **cuando** el Administrador abre el detalle del tipo, **entonces** ve las hojas reconocidas, y las columnas de cada hoja con sus nombres y en el mismo orden en que aparecen en el archivo.
- **Dado** un formato cargado, **cuando** el Administrador compara lo reconocido con el archivo original, **entonces** no encuentra secciones, hojas ni columnas agregadas, renombradas, eliminadas ni reordenadas por el sistema.
- **Dado** un formato del que no se logra reconocer ninguna sección, hoja ni columna, **cuando** termina el análisis, **entonces** el sistema se lo informa al Administrador y no deja el tipo disponible para los RO.
- **Dado** un tipo con su formato ya cargado, **cuando** el Administrador vuelve a abrir su detalle en otro momento, **entonces** ve exactamente la misma estructura, sin que el sistema vuelva a analizar el archivo.

### HU-4: Mantener los tipos de documentación
**Como** Administrador, **quiero** corregir, desactivar y eliminar tipos de documentación, **para** que la lista que ven los RO refleje lo que el área realmente usa hoy.

**Criterios de aceptación:**
- **Dado** un tipo existente, **cuando** el Administrador cambia su nombre o su descripción, **entonces** el cambio queda guardado y la estructura reconocida de su formato no se altera.
- **Dado** un tipo existente, **cuando** el Administrador reemplaza su formato por otro archivo válido, **entonces** el sistema reconoce la estructura del nuevo archivo y, desde ese momento, es esa la que manda.
- **Dado** un tipo existente, **cuando** el Administrador intenta reemplazar su formato por un archivo inválido, **entonces** el tipo conserva el formato y la estructura que ya tenía.
- **Dado** un tipo activo, **cuando** el Administrador lo desactiva, **entonces** deja de aparecer entre las opciones que puede elegir un RO, pero sigue visible para el Administrador y puede reactivarse.
- **Dado** un tipo que nunca ha sido usado, **cuando** el Administrador lo elimina, **entonces** desaparece de la plataforma.
- **Dado** un tipo que ya fue usado por algún RO, **cuando** el Administrador intenta eliminarlo, **entonces** el sistema no lo elimina, le explica que está en uso y le ofrece desactivarlo.

### HU-5: Elegir entre los tipos disponibles
**Como** RO, **quiero** ver la lista de tipos de documentación disponibles con su descripción, **para** saber qué puedo documentar en la plataforma y elegir el que corresponde a mi actividad.

**Criterios de aceptación:**
- **Dado** un RO autenticado, **cuando** consulta los tipos de documentación, **entonces** ve únicamente los tipos activos y con formato cargado, con su nombre y su descripción.
- **Dado** un tipo incompleto o desactivado, **cuando** un RO consulta los tipos de documentación, **entonces** ese tipo no aparece entre los que puede elegir.
- **Dado** que no hay ningún tipo disponible, **cuando** un RO consulta la lista, **entonces** el sistema se lo indica explícitamente y le señala que debe solicitarlo al Administrador, en vez de mostrarle una pantalla vacía.

## 4. Requerimientos funcionales

| ID | Requerimiento |
|---|---|
| RF-01 | El sistema debe permitir al **Administrador** crear tipos de documentación, y debe impedir esa acción a cualquier usuario con rol RO (Art. X, funcionalidad 001). |
| RF-02 | El sistema debe registrar para cada tipo de documentación, como mínimo: nombre, descripción y estado. El nombre debe ser único entre los tipos existentes. |
| RF-03 | El sistema debe distinguir tres estados de un tipo: **incompleto** (sin formato cargado), **activo** (con formato cargado y disponible para los RO) y **desactivado** (no disponible para los RO, conservado para el Administrador). |
| RF-04 | El sistema debe permitir cargar, para cada tipo, **un** archivo de formato en Word o Excel, y debe rechazar cualquier otro tipo de archivo indicando cuáles admite. |
| RF-05 | El sistema debe **reconocer la estructura** del formato al cargarlo: en Word, las secciones con sus nombres y su orden; en Excel, las hojas con su orden, y las columnas de cada hoja con sus nombres y su orden. |
| RF-06 | El sistema debe conservar la estructura reconocida **tal como viene en el archivo**: no agrega, quita, renombra ni reordena secciones, hojas ni columnas (Art. I). |
| RF-07 | El sistema debe analizar cada formato **una sola vez**, en el momento de cargarlo, y guardar el resultado para que las funcionalidades posteriores lo consulten sin volver a procesar el archivo (Art. VI). |
| RF-08 | El sistema debe mostrar al Administrador la estructura reconocida de un tipo, de modo que pueda compararla con el archivo original antes de ponerlo a disposición de los RO. |
| RF-09 | El sistema debe conservar el archivo de formato original asociado al tipo, porque el documento final se entrega en ese mismo formato (funcionalidad 006). |
| RF-10 | El sistema debe rechazar un formato que no pueda interpretar —archivo dañado, protegido o sin ninguna estructura reconocible— informando el motivo, y debe dejar el tipo en el estado en que estaba antes del intento. |
| RF-11 | El sistema no debe completar ni suponer nada sobre el formato: si una sección, hoja o columna no tiene nombre en el archivo, se registra como viene y no se le inventa uno (Art. II). |
| RF-12 | El sistema debe permitir al Administrador **modificar** el nombre y la descripción de un tipo sin alterar la estructura reconocida de su formato. |
| RF-13 | El sistema debe permitir al Administrador **reemplazar** el formato de un tipo; al hacerlo, reconoce la estructura del nuevo archivo y esa pasa a ser la vigente. |
| RF-14 | El sistema debe permitir al Administrador **desactivar** y **reactivar** un tipo. Un tipo desactivado no aparece entre las opciones de los RO. |
| RF-15 | El sistema debe permitir **eliminar** únicamente los tipos que nunca han sido usados, y debe impedir la eliminación de un tipo en uso, ofreciendo desactivarlo en su lugar. |
| RF-16 | El sistema debe ofrecer a los RO la lista de tipos **activos**, con nombre y descripción, y debe excluir de ella los tipos incompletos y los desactivados. |
| RF-17 | El sistema debe funcionar con **cualquier** formato Word o Excel que cargue el Administrador, sin depender del caso de referencia (Adapter Reverso) ni de nombres de sección predefinidos (Art. VIII). |
| RF-18 | Los límites de la carga —tamaño máximo del archivo y extensiones admitidas— deben ser configuración, no valores fijos en el código (Art. V). |

## 5. Entradas y salidas

| Tipo | Elemento | Formato | Origen / destino |
|---|---|---|---|
| Entrada | Nombre y descripción del tipo de documentación | Datos ingresados en la administración de tipos | El Administrador |
| Entrada | Archivo de formato del tipo | `.docx` / `.xlsx` (extensiones exactas por confirmar, ver sección 9) | El Administrador |
| Entrada | Cambios sobre un tipo existente: nombre, descripción, formato reemplazado, desactivación, reactivación o eliminación | Acciones en la administración de tipos | El Administrador |
| Salida | Estructura reconocida del formato: secciones, hojas y columnas, con sus nombres y su orden | Representación interna consultable por la plataforma | Las funcionalidades 004, 005 y 006 |
| Salida | Vista de la estructura reconocida | Pantalla de detalle del tipo | El Administrador |
| Salida | Listado de tipos con su estado | Pantalla de administración de tipos | El Administrador |
| Salida | Lista de tipos disponibles con nombre y descripción | Pantalla de la plataforma | El RO (y la funcionalidad 003, que parte de esa elección) |
| Salida | Archivo de formato original conservado | `.docx` / `.xlsx` | La funcionalidad 006, que entrega el documento en ese formato |
| Salida | Mensaje de rechazo con su motivo | Mensaje en pantalla | El Administrador que intentó la carga |

## 6. Casos borde y errores

- **Tipo creado sin formato:** queda **incompleto**. El Administrador lo ve así en su listado y ningún RO puede elegirlo (RF-03, RF-16).
- **Nombre de tipo repetido:** no se crea y se indica el motivo (RF-02). Lo mismo al renombrar un tipo existente con el nombre de otro.
- **Archivo que no es Word ni Excel:** se rechaza indicando qué formatos se admiten; el tipo no cambia de estado (RF-04).
- **Archivo dañado, protegido con contraseña o ilegible:** se rechaza con su motivo. El tipo conserva el formato que tenía antes, o sigue incompleto si no tenía (RF-10).
- **Archivo válido del que no se reconoce ninguna sección, hoja ni columna:** se informa al Administrador y el tipo no queda disponible para los RO. Un formato sin estructura reconocida no sirve para generar nada.
- **Formato con secciones, hojas o columnas de nombre repetido:** se conservan todas, tal como vienen, sin fusionarlas ni renumerarlas. El orden las distingue (Art. I, RF-06).
- **Formato con una sección, hoja o columna sin nombre:** se registra como viene, sin inventarle un nombre (RF-11).
- **Archivo que supera el tamaño admitido:** se rechaza indicando el límite (RF-18).
- **Reemplazo del formato de un tipo que ya se usó:** el efecto sobre las actividades y los documentos existentes es un pendiente de esta spec (ver sección 9).
- **Eliminación de un tipo en uso:** no se permite; se ofrece desactivarlo (RF-15).
- **Desactivación de un tipo que un RO tiene abierto en ese momento:** el tipo deja de ofrecerse para nuevas actividades. Qué pasa con una actividad ya abierta lo define la funcionalidad 003, que es la que introduce la actividad; esta spec no la conoce.
- **Dos Administradores cargando formato al mismo tipo a la vez:** solo una de las cargas queda vigente; el tipo no puede quedar con la estructura de un archivo y el archivo de otro.
- **Ningún tipo disponible cuando un RO consulta la lista:** se le indica explícitamente, no se le muestra una pantalla vacía (HU-5).

## 7. Fuera de alcance

- La **apertura de actividades** y la carga de la información del RO contra un tipo elegido (funcionalidad 003). Aquí solo se entrega la lista de tipos disponibles.
- El **análisis de faltantes y las preguntas al RO** (004), la **generación y la evaluación** del documento (005) y el **historial y la descarga** (006). Esta spec deja lista la estructura que todas ellas usan, y nada más.
- Los **parámetros del sistema** —rúbrica, pesos, puntaje mínimo, iteraciones y modelo por tarea— (funcionalidad 007), incluida la configuración del modelo que intervenga en el reconocimiento del formato.
- La **edición manual de la estructura reconocida** por parte del Administrador: en esta spec el Administrador la revisa y, si no corresponde, corrige el archivo y lo vuelve a cargar (ver también sección 9).
- La **creación o el diseño de formatos** dentro de la plataforma: los formatos se cargan ya hechos, no se construyen aquí.
- Formatos distintos de Word y Excel (PDF, presentaciones, texto plano, formularios web).
- **Varios formatos para un mismo tipo** o selección entre variantes: un tipo tiene un formato vigente (RF-04).
- **Permisos por tipo de documentación** (que un RO vea unos tipos y no otros): todos los RO ven todos los tipos activos. Los roles siguen siendo los dos de la funcionalidad 001.
- **Registro de auditoría** de quién creó o cambió cada tipo: coherente con lo decidido en la funcionalidad 001, no se requiere por ahora.
- La **retención y eliminación** de los archivos de formato cargados, pendiente abierto del Artículo X.4 de la constitución.

## 8. Criterios de éxito medibles

- **0 diferencias** entre la estructura reconocida y la del archivo original —en nombres, en cantidad y en orden de secciones, hojas y columnas— verificado en al menos tres formatos distintos.
- La funcionalidad se verifica con **al menos dos formatos ajenos al caso de referencia**: un Word ficticio y un Excel ficticio, además del Adapter Reverso (Art. VIII). Los casos de prueba usan solo datos ficticios (Art. X.3).
- **1 sola vez** se analiza cada formato: consultar el detalle de un tipo o usarlo en una generación posterior no vuelve a procesar el archivo (Art. VI, RF-07).
- **0 elementos inventados:** ninguna sección, hoja o columna aparece en la estructura reconocida sin existir en el archivo, ni recibe un nombre que el archivo no traía.
- **0 opciones** de administración de tipos visibles o alcanzables para un usuario con rol RO, incluyendo intentos de acceso directo.
- **100 % de las cargas inválidas** —extensión no admitida, archivo dañado, archivo protegido, sin estructura reconocible, tamaño excedido— se rechazan con un motivo y dejan el tipo en el estado que tenía antes del intento.
- **0 tipos incompletos o desactivados** aparecen entre las opciones que puede elegir un RO.
- Cambiar las extensiones admitidas y el tamaño máximo de carga se logra **sin modificar código** (RF-18).

## 9. Pendientes y preguntas abiertas

> Todo lo que no se sabe se marca aquí como `[NECESITA ACLARACIÓN: ...]`. La spec no pasa a planificación con aclaraciones abiertas que afecten el alcance.

- [NECESITA ACLARACIÓN: cuando el Administrador reemplaza el formato de un tipo que ya tiene actividades o documentos generados, ¿qué debe pasar con ellos? Opciones: (a) el tipo guarda versiones de su formato y cada actividad queda atada a la versión con la que nació; (b) solo existe el formato vigente y lo anterior queda desactualizado; (c) no se permite reemplazar el formato de un tipo en uso y en su lugar se crea un tipo nuevo. La respuesta cambia el alcance: la opción (a) agrega versionado de formatos a esta funcionalidad.]
- [NECESITA ACLARACIÓN: si el Administrador revisa la estructura reconocida y no corresponde a lo que esperaba, ¿debe poder corregirla dentro de la plataforma —renombrar, reordenar o marcar elementos— o su única vía es corregir el archivo y volverlo a cargar? Esta spec asume lo segundo (sección 7). Permitir la corrección manual agrega una pantalla de edición de estructura y obliga a definir cómo convive con el Artículo I.]
- [NECESITA ACLARACIÓN: ¿qué extensiones exactas se admiten y cuál es el tamaño máximo de un formato? Esta spec asume los formatos actuales de Office (`.docx` y `.xlsx`) y deja el límite como configuración (RF-18). Falta confirmar si deben admitirse también los formatos antiguos (`.doc`, `.xls`) y cuál es el tamaño máximo razonable para los formatos que hoy usa el área.]
- **PENDIENTE (constitución, Art. X.4)** — tiempo de retención y eliminación de los archivos cargados. Aplica también a los archivos de formato de esta funcionalidad. Fuera del alcance de esta spec.

## 10. Verificación contra la constitución

- [x] Respeta la estructura de los formatos definidos (Art. I) — es el eje de la funcionalidad: la estructura se reconoce y se conserva tal como viene, sin agregar, quitar, renombrar ni reordenar nada (RF-05, RF-06), y el Administrador puede comprobarlo (RF-08).
- [x] No exige completar datos que no estén en los insumos ni en las respuestas del RO (Art. II y III) — el sistema no inventa nombres de secciones, hojas ni columnas; lo que no viene en el archivo no se completa (RF-11). Esta funcionalidad no le pide información al RO.
- [x] Contempla al menos un caso distinto al de referencia (Art. VIII) — se verifica con un Word ficticio y un Excel ficticio además del Adapter Reverso, y ningún nombre de sección queda predefinido en la plataforma (RF-17, sección 8).
- [x] No define tecnologías ni implementación (Art. XI) — no se menciona ningún mecanismo de lectura de archivos, almacenamiento ni estructura de código; el *cómo* queda para `plan.md`.
- [x] Analiza cada formato una sola vez (Art. VI) — RF-07 y el criterio correspondiente de la sección 8.
- [x] Valores editables fuera del código (Art. V) — extensiones admitidas y tamaño máximo son configuración (RF-18).

## Registro de aclaraciones

| Fecha | Pregunta | Respuesta |
|---|---|---|
| — | — | Sin aclaraciones resueltas todavía. Las tres marcas abiertas están en la sección 9. |
