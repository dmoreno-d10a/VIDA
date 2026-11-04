# Especificación: Tipos de documentación

**ID:** 002
**Rama:** `feature/002-tipos-de-documentacion`
**Autor:** Diego Moreno
**Fecha:** 2026-10-26
**Estado:** En revisión

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
- **Dado** un tipo existente, **cuando** el Administrador reemplaza su formato por otro archivo válido, **entonces** el sistema reconoce la estructura del nuevo archivo, la registra como una **versión nueva** del formato del tipo, y desde ese momento es esa la vigente.
- **Dado** un tipo cuyo formato se reemplazó, **cuando** el Administrador consulta su detalle, **entonces** ve el historial de versiones del formato, con cuál es la vigente y desde cuándo.
- **Dado** un tipo cuyo formato se reemplazó, **cuando** se consulta una versión anterior, **entonces** siguen disponibles su estructura reconocida y su archivo original, sin volver a analizarlos.
- **Dado** un tipo existente, **cuando** el Administrador intenta reemplazar su formato por un archivo inválido, **entonces** el tipo conserva el formato y la estructura que ya tenía.
- **Dado** un tipo activo, **cuando** el Administrador lo desactiva, **entonces** deja de aparecer entre las opciones que puede elegir un RO, pero sigue visible para el Administrador y puede reactivarse.
- **Dado** un tipo que nunca ha sido usado, **cuando** el Administrador lo elimina, **entonces** desaparece de la plataforma.
- **Dado** un tipo que ya fue usado por algún RO, **cuando** el Administrador intenta eliminarlo, **entonces** el sistema no lo elimina, le explica que está en uso y le ofrece desactivarlo.
- **Dado** un tipo con formato cargado al que todavía no ha recurrido ningún RO, **cuando** el Administrador intenta eliminarlo, **entonces** el sistema tampoco lo elimina y le ofrece desactivarlo (RF-15a).

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
| RF-02 | El sistema debe registrar para cada tipo de documentación, como mínimo: nombre, descripción y estado. El nombre debe ser único entre los tipos existentes, puede medir hasta **200 caracteres**, y la descripción hasta **1000**. |
| RF-02a | Un nombre de tipo es válido cuando no queda vacío al quitar los espacios de los extremos; el sistema lo **guarda tal como lo escribió** el Administrador. Para decidir si dos nombres están repetidos los compara **sin distinguir mayúsculas** y sin esos espacios, pero **los acentos sí distinguen**: «Adapter Reverso» y «adapter reverso» son el mismo nombre, «Factura» y «Fáctura» no. |
| RF-03 | El sistema debe distinguir tres estados de un tipo: **incompleto** (sin formato cargado), **activo** (con formato cargado y disponible para los RO) y **desactivado** (no disponible para los RO, conservado para el Administrador). |
| RF-04 | El sistema debe permitir cargar, para cada tipo, **un** archivo de formato vigente en Word (`.docx`) o Excel (`.xlsx`), y debe rechazar cualquier otro tipo de archivo —incluidos los formatos antiguos `.doc` y `.xls`— indicando cuáles admite. |
| RF-05 | El sistema debe **reconocer la estructura** del formato al cargarlo: en Word, las secciones con sus nombres y su orden; en Excel, las hojas con su orden, y las columnas de cada hoja con sus nombres y su orden. |
| RF-05a | En Word, una **sección** es un párrafo con estilo de título (`Título 1` a `Título 9` y sus equivalentes en otros idiomas), y se registra con su nombre y su nivel. Ninguna otra marca —negrita, tamaño de letra, numeración manual— cuenta como sección: interpretarla sería suponer (Art. II). |
| RF-05b | En Excel, los nombres de las columnas se toman de la **primera fila con contenido** de cada hoja, y el sistema registra de qué fila los tomó, para que el Administrador pueda confirmarlo (RF-08). |
| RF-06 | El sistema debe conservar la estructura reconocida **tal como viene en el archivo**: no agrega, quita, renombra ni reordena secciones, hojas ni columnas (Art. I). |
| RF-07 | El sistema debe analizar cada formato **una sola vez**, en el momento de cargarlo, y guardar el resultado para que las funcionalidades posteriores lo consulten sin volver a procesar el archivo (Art. VI). |
| RF-08 | El sistema debe mostrar al Administrador la estructura reconocida de un tipo, de modo que pueda compararla con el archivo original antes de ponerlo a disposición de los RO. |
| RF-09 | El sistema debe conservar el archivo de formato original asociado al tipo, porque el documento final se entrega en ese mismo formato (funcionalidad 006). |
| RF-10 | El sistema debe rechazar un formato que no pueda interpretar —archivo dañado, protegido o sin ninguna estructura reconocible— informando el motivo, y debe dejar el tipo en el estado en que estaba antes del intento. |
| RF-11 | El sistema no debe completar ni suponer nada sobre el formato: si una sección, hoja o columna no tiene nombre en el archivo, se registra como viene y no se le inventa uno (Art. II). |
| RF-12 | El sistema debe permitir al Administrador **modificar** el nombre y la descripción de un tipo sin alterar la estructura reconocida de su formato. |
| RF-13 | El sistema debe permitir al Administrador **reemplazar** el formato de un tipo; al hacerlo, reconoce la estructura del nuevo archivo, la registra como una versión nueva y esa pasa a ser la vigente (ver RF-19 a RF-21). |
| RF-14 | El sistema debe permitir al Administrador **desactivar** y **reactivar** un tipo. Un tipo desactivado no aparece entre las opciones de los RO. |
| RF-15 | El sistema debe permitir **eliminar** únicamente los tipos que nunca han sido usados, y debe impedir la eliminación de un tipo en uso, ofreciendo desactivarlo en su lugar. |
| RF-15a | Mientras no exista la actividad (funcionalidad 003), «nunca usado» significa **sin formato vigente**: un tipo incompleto no pudo ser elegido por ningún RO. Un tipo con formato cargado no se elimina, aunque todavía no lo haya usado nadie. Cuando la 003 introduzca la actividad, la regla se podrá ampliar. |
| RF-16 | El sistema debe ofrecer a los RO la lista de tipos **activos**, con nombre y descripción, y debe excluir de ella los tipos incompletos y los desactivados. |
| RF-17 | El sistema debe funcionar con **cualquier** formato Word o Excel que cargue el Administrador, sin depender del caso de referencia (Adapter Reverso) ni de nombres de sección predefinidos (Art. VIII). |
| RF-18 | Los límites de la carga —tamaño máximo del archivo y extensiones admitidas— deben ser configuración, no valores fijos en el código (Art. V). El tamaño máximo por defecto es **25 MB**. |
| RF-19 | El sistema debe **versionar** el formato de cada tipo: cada carga o reemplazo produce una versión, y el tipo tiene en todo momento una sola versión **vigente**. |
| RF-20 | El sistema debe conservar, de cada versión del formato, su **archivo original** y su **estructura reconocida**, y debe poder identificar cada versión de forma estable, para que las funcionalidades posteriores puedan atar un documento generado a la versión con la que se produjo (Art. IX). |
| RF-21 | El sistema debe mostrar al Administrador el **historial de versiones** del formato de un tipo, indicando cuál es la vigente y desde cuándo, y permitirle consultar la estructura reconocida de una versión anterior. |

## 5. Entradas y salidas

| Tipo | Elemento | Formato | Origen / destino |
|---|---|---|---|
| Entrada | Nombre y descripción del tipo de documentación | Datos ingresados en la administración de tipos | El Administrador |
| Entrada | Archivo de formato del tipo | `.docx` / `.xlsx`, hasta el tamaño máximo configurado (RF-18) | El Administrador |
| Entrada | Cambios sobre un tipo existente: nombre, descripción, formato reemplazado, desactivación, reactivación o eliminación | Acciones en la administración de tipos | El Administrador |
| Salida | Estructura reconocida del formato: secciones, hojas y columnas, con sus nombres y su orden | Representación interna consultable por la plataforma | Las funcionalidades 004, 005 y 006 |
| Salida | Vista de la estructura reconocida | Pantalla de detalle del tipo | El Administrador |
| Salida | Historial de versiones del formato, con la vigente señalada | Pantalla de detalle del tipo | El Administrador |
| Salida | Listado de tipos con su estado | Pantalla de administración de tipos | El Administrador |
| Salida | Lista de tipos disponibles con nombre y descripción | Pantalla de la plataforma | El RO (y la funcionalidad 003, que parte de esa elección) |
| Salida | Archivo de formato original conservado, por versión | `.docx` / `.xlsx` | La funcionalidad 006, que entrega el documento en ese formato |
| Salida | Mensaje de rechazo con su motivo | Mensaje en pantalla | El Administrador que intentó la carga |

## 6. Entidades principales

Los tres conceptos que esta funcionalidad introduce en la plataforma. Se describen por lo que
**son** y por lo que el negocio exige de ellos; su forma concreta la define `plan.md`.

- **Tipo de documentación.** Una clase de documento que la plataforma puede generar: tiene un
  nombre único, una descripción y un estado (incompleto, activo o desactivado). Es lo que el RO
  elige al abrir una actividad. Un tipo sin formato cargado no sirve para nada todavía, y por eso
  existe el estado incompleto.
- **Versión del formato.** Cada archivo de formato que el Administrador carga para un tipo, con
  la estructura que se le reconoció y el momento en que entró. Un tipo tiene **una sola versión
  vigente** y conserva las anteriores sin alterarlas. Una versión no se edita ni se borra: es el
  registro de qué estructura mandaba en un momento dado, y reescribirla borraría la trazabilidad
  del documento que se generó con ella (Art. IX).
- **Estructura reconocida.** La forma del formato tal como viene en el archivo: en Word, las
  secciones con su nombre, su nivel y su orden; en Excel, las hojas con su orden y las columnas de
  cada hoja con su nombre y su orden. Es lo que las funcionalidades 004, 005 y 006 consumen, y
  pertenece a una versión, no al tipo. Su contenido no se interpreta ni se completa: lo que no
  está en el archivo no está en ella (Art. I, Art. II).

## 7. Casos borde y errores

- **Tipo creado sin formato:** queda **incompleto**. El Administrador lo ve así en su listado y ningún RO puede elegirlo (RF-03, RF-16).
- **Nombre de tipo repetido:** no se crea y se indica el motivo (RF-02). Lo mismo al renombrar un tipo existente con el nombre de otro.
- **Archivo que no es Word ni Excel:** se rechaza indicando qué formatos se admiten; el tipo no cambia de estado (RF-04).
- **Archivo dañado, protegido con contraseña o ilegible:** se rechaza con su motivo. El tipo conserva el formato que tenía antes, o sigue incompleto si no tenía (RF-10).
- **Archivo válido del que no se reconoce ninguna sección, hoja ni columna:** se informa al Administrador y el tipo no queda disponible para los RO. Un formato sin estructura reconocida no sirve para generar nada.
- **Word que marca sus secciones con negrita o tamaño de letra, sin estilos de título:** se rechaza como «sin estructura reconocible», y el mensaje dice que se esperaban estilos de título, para que el Administrador los aplique y lo vuelva a cargar (RF-05a). El sistema no intenta deducir qué párrafo era un título.
- **Hoja de Excel cuya primera fila con contenido es un título o un logo, no los encabezados:** se toma esa fila como encabezados, porque es la regla (RF-05b), y el Administrador lo ve en la pantalla de detalle. Si no corresponde, corrige el archivo y lo vuelve a cargar.
- **Formato con secciones, hojas o columnas de nombre repetido:** se conservan todas, tal como vienen, sin fusionarlas ni renumerarlas. El orden las distingue (Art. I, RF-06).
- **Formato con una sección, hoja o columna sin nombre:** se registra como viene, sin inventarle un nombre (RF-11).
- **Archivo que supera el tamaño admitido:** se rechaza indicando el límite (RF-18).
- **Reemplazo del formato de un tipo que ya se usó:** el formato nuevo queda como versión vigente y **no altera** las versiones anteriores ni lo que se generó con ellas. Un documento ya producido se sigue explicando contra la versión con la que nació (RF-19, RF-20). Atar cada actividad a una versión le corresponde a la funcionalidad 003, que es la que introduce la actividad; esta spec le entrega la versión identificable.
- **Reemplazo por un archivo idéntico al vigente:** se registra como una versión nueva igual que cualquier otra. Esta spec no compara contenidos para decidir si un archivo cambió o no: eso sería suponer (Art. II).
- **Estructura reconocida que no corresponde a lo esperado:** el Administrador corrige el archivo y lo vuelve a cargar, lo que produce otra versión. La plataforma no permite editar la estructura reconocida (sección 8).
- **Eliminación de un tipo en uso:** no se permite; se ofrece desactivarlo (RF-15).
- **Desactivación de un tipo que un RO tiene abierto en ese momento:** el tipo deja de ofrecerse para nuevas actividades. Qué pasa con una actividad ya abierta lo define la funcionalidad 003, que es la que introduce la actividad; esta spec no la conoce.
- **Dos Administradores cargando formato al mismo tipo a la vez:** solo una de las cargas queda vigente; el tipo no puede quedar con la estructura de un archivo y el archivo de otro.
- **Ningún tipo disponible cuando un RO consulta la lista:** se le indica explícitamente, no se le muestra una pantalla vacía (HU-5).

## 8. Fuera de alcance

- La **apertura de actividades** y la carga de la información del RO contra un tipo elegido (funcionalidad 003). Aquí solo se entrega la lista de tipos disponibles.
- El **análisis de faltantes y las preguntas al RO** (004), la **generación y la evaluación** del documento (005) y el **historial y la descarga** (006). Esta spec deja lista la estructura que todas ellas usan, y nada más.
- Los **parámetros del sistema** —rúbrica, pesos, puntaje mínimo, iteraciones y modelo por tarea— (funcionalidad 007), incluida la configuración del modelo que intervenga en el reconocimiento del formato.
- La **edición manual de la estructura reconocida** por parte del Administrador: la revisa y, si no corresponde, corrige el archivo y lo vuelve a cargar. Permitir editarla dentro de la plataforma dejaría que la estructura guardada divergiera del archivo, que es justo lo que el Art. I no admite.
- La **creación o el diseño de formatos** dentro de la plataforma: los formatos se cargan ya hechos, no se construyen aquí.
- Formatos distintos de Word y Excel (PDF, presentaciones, texto plano, formularios web).
- **Varios formatos vigentes a la vez** para un mismo tipo, o que el RO elija entre variantes: un tipo tiene una sola versión vigente (RF-04, RF-19). El historial de versiones sí está dentro del alcance, pero solo la vigente se usa para generar.
- **Permisos por tipo de documentación** (que un RO vea unos tipos y no otros): todos los RO ven todos los tipos activos. Los roles siguen siendo los dos de la funcionalidad 001.
- **Registro de auditoría** de quién creó o cambió cada tipo: coherente con lo decidido en la funcionalidad 001, no se requiere por ahora.
- La **retención y eliminación** de los archivos de formato cargados, pendiente abierto del Artículo X.4 de la constitución.

## 9. Criterios de éxito medibles

- **CE-01 · 0 diferencias** entre la estructura reconocida y la del archivo original —en nombres, en cantidad y en orden de secciones, hojas y columnas— verificado en al menos tres formatos distintos.
- **CE-02 ·** la funcionalidad se verifica con **al menos dos formatos ajenos al caso de referencia**: un Word ficticio y un Excel ficticio, además del Adapter Reverso (Art. VIII). Los casos de prueba usan solo datos ficticios (Art. X.3).
- **CE-03 · 1 sola vez** se analiza cada formato: consultar el detalle de un tipo o usarlo en una generación posterior no vuelve a procesar el archivo (Art. VI, RF-07).
- **CE-04 · 0 elementos inventados:** ninguna sección, hoja o columna aparece en la estructura reconocida sin existir en el archivo, ni recibe un nombre que el archivo no traía.
- **CE-05 · 0 opciones** de administración de tipos visibles o alcanzables para un usuario con rol RO, incluyendo intentos de acceso directo.
- **CE-06 · 100 % de las cargas inválidas** —extensión no admitida, archivo dañado, archivo protegido, sin estructura reconocible, tamaño excedido— se rechazan con un motivo y dejan el tipo en el estado que tenía antes del intento.
- **CE-07 · 0 tipos incompletos o desactivados** aparecen entre las opciones que puede elegir un RO.
- **CE-08 ·** cambiar las extensiones admitidas y el tamaño máximo de carga se logra **sin modificar código** (RF-18).
- **CE-09 · 30 segundos** es el techo de la carga completa para cualquier archivo dentro del tamaño admitido, incluido el de 25 MB. Se resuelve en la misma petición: no hay procesamiento en segundo plano. Se mide **punta a punta**: desde que el Administrador confirma la carga hasta que ve la estructura reconocida en pantalla, con la subida del archivo por la red incluida, en una conexión de la red del área. Es el tiempo que él espera, no el que el servidor tarda en procesar.
- **CE-10 · 0 pérdidas al reemplazar:** tras reemplazar el formato de un tipo tres veces, las tres versiones anteriores conservan su archivo original y su estructura reconocida, y se puede decir cuál estaba vigente en cada momento (RF-19, RF-20).

## 10. Pendientes y preguntas abiertas

> Todo lo que no se sabe se marca aquí como `[NECESITA ACLARACIÓN: ...]`. La spec no pasa a planificación con aclaraciones abiertas que afecten el alcance.

**No quedan aclaraciones abiertas.** Hubo dos pasadas: tres aclaraciones el 2026-11-03 y cuatro más el 2026-11-04, todas en el registro al final de este documento.

De la primera pasada:

- El formato de un tipo se **versiona** (RF-19 a RF-21). Fue la decisión que más alcance agregó.
- La estructura reconocida **no se edita** dentro de la plataforma: se corrige el archivo y se recarga (sección 8).
- Se admiten **solo `.docx` y `.xlsx`**, con un tamaño máximo por defecto de **25 MB**, configurable (RF-04, RF-18).

De la segunda pasada, que cerró lo que el plan había tenido que suponer:

- Una **sección** de Word es un párrafo con estilo de título, y nada más (RF-05a).
- Los **encabezados** de una hoja de Excel salen de su primera fila con contenido (RF-05b).
- **Eliminar** solo alcanza a los tipos sin formato vigente, mientras no exista la actividad (RF-15a).
- La carga completa tiene un techo de **30 segundos** y se resuelve en la misma petición (sección 9).

De la tercera pasada, que cerró los vacíos que la checklist de requisitos había encontrado:

- El nombre mide hasta **200 caracteres** y la descripción hasta **1000** (RF-02).
- Un nombre es válido si no queda vacío al quitar espacios, y los nombres repetidos se comparan **sin mayúsculas pero con acentos** (RF-02a).
- Los **30 segundos** se miden **punta a punta**, con la red incluida (sección 9).

Queda un pendiente que no es de esta spec:

- **PENDIENTE (constitución, Art. X.4)** — tiempo de retención y eliminación de los archivos cargados. Aplica también a los archivos de formato de esta funcionalidad, y ahora a sus versiones anteriores. Se resuelve enmendando la constitución, no aquí.

## 11. Verificación contra la constitución

- [x] Respeta la estructura de los formatos definidos (Art. I) — es el eje de la funcionalidad: la estructura se reconoce y se conserva tal como viene, sin agregar, quitar, renombrar ni reordenar nada (RF-05, RF-06), y el Administrador puede comprobarlo (RF-08).
- [x] No exige completar datos que no estén en los insumos ni en las respuestas del RO (Art. II y III) — el sistema no inventa nombres de secciones, hojas ni columnas; lo que no viene en el archivo no se completa (RF-11). Esta funcionalidad no le pide información al RO.
- [x] Contempla al menos un caso distinto al de referencia (Art. VIII) — se verifica con un Word ficticio y un Excel ficticio además del Adapter Reverso, y ningún nombre de sección queda predefinido en la plataforma (RF-17, sección 9).
- [x] No define tecnologías ni implementación (Art. XI) — no se menciona ningún mecanismo de lectura de archivos, almacenamiento ni estructura de código; el *cómo* queda para `plan.md`.
- [x] Analiza cada formato una sola vez (Art. VI) — RF-07 y el criterio correspondiente de la sección 9.
- [x] Valores editables fuera del código (Art. V) — extensiones admitidas y tamaño máximo son configuración (RF-18).
- [x] Trazabilidad (Art. IX) — el versionado del formato es lo que permite rastrear un documento generado hasta la estructura exacta que lo produjo, incluso después de que el Administrador reemplace el formato (RF-19, RF-20).

## Registro de aclaraciones

| Fecha | Pregunta | Respuesta |
|---|---|---|
| 2026-11-03 | Al reemplazar el formato de un tipo que ya tiene actividades o documentos generados, ¿qué pasa con ellos? | El formato se **versiona**: cada carga produce una versión, el tipo tiene una sola vigente, y las anteriores conservan su archivo y su estructura. Razón: el Art. IX exige que un documento entregado se pueda rastrear al formato exacto que lo produjo. Agrega RF-19 a RF-21 al alcance. |
| 2026-11-03 | Si la estructura reconocida no corresponde a lo esperado, ¿el Administrador puede corregirla en la plataforma? | **No.** Corrige el archivo y lo vuelve a cargar. Razón: editarla dentro de la plataforma permitiría que la estructura guardada divergiera del archivo, que es lo que el Art. I no admite. Sin cambio de alcance. |
| 2026-11-03 | ¿Qué extensiones se admiten y cuál es el tamaño máximo? | Solo **`.docx` y `.xlsx`**; los antiguos `.doc` y `.xls` se rechazan. Tamaño máximo por defecto **25 MB**, configurable. Razón: los formatos actuales de Office se leen de forma predecible, y ahí el Art. I no admite errores. Afina RF-04 y RF-18. |
| 2026-11-04 | ¿Qué marca una sección dentro de un Word? | **Solo los estilos de título** (`Título 1` a `Título 9`). Ninguna otra marca cuenta. Razón: es determinista y no puede inventar (Art. II); una heurística sobre negritas metería como sección un párrafo que no lo era. Agrega RF-05a. |
| 2026-11-04 | ¿De qué fila de una hoja de Excel salen los nombres de las columnas? | De la **primera fila con contenido**, registrando cuál fue para que el Administrador lo confirme. Razón: muchos formatos traen un título o un logo arriba, y fijar la fila 1 rechazaría formatos legítimos. Agrega RF-05b. |
| 2026-11-04 | Sin la actividad (003), el sistema no puede saber si un RO usó un tipo. ¿Qué se puede eliminar hoy? | Solo los tipos **sin formato vigente**. Razón: es lo único de lo que se puede afirmar con certeza que ningún RO lo eligió; la regla se amplía cuando la 003 traiga la actividad. Agrega RF-15a. |
| 2026-11-04 | ¿Cuánto puede tardar la carga y el análisis de un formato? | Techo de **30 segundos** para cualquier archivo dentro del tamaño admitido, resuelto **en la misma petición**. Razón: cubre con certeza el caso de 25 MB sin introducir procesamiento en segundo plano, que traería complejidad que nadie pidió. Agrega un criterio medible a la sección 9. |
| 2026-11-04 | ¿Cuánto pueden medir el nombre y la descripción de un tipo? | **200 y 1000 caracteres.** Razón: deja espacio para un nombre descriptivo sin que el listado se vuelva ilegible, y da algo concreto que validar. Afina RF-02. |
| 2026-11-04 | ¿Qué es un nombre válido, y cómo se comparan dos nombres para ver si están repetidos? | Válido si **no queda vacío** al quitar los espacios de los extremos. Se comparan **sin distinguir mayúsculas** y sin esos espacios; **los acentos sí distinguen**. Razón: para el Administrador «Adapter Reverso» y «adapter reverso» son el mismo tipo, mientras que igualar acentos exigiría una capacidad extra del motor de base de datos para un error poco probable. Agrega RF-02a. |
| 2026-11-04 | ¿Dónde se miden los 30 segundos de la carga? | **Punta a punta**, desde que el Administrador confirma hasta que ve la estructura en pantalla, con la subida por la red incluida. Razón: es el tiempo que él espera; medir solo el proceso en el servidor daría un número bueno con una espera mala, y con 25 MB la red pesa. Afina el criterio CE-09. |
