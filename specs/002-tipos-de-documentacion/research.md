# Investigación: Tipos de documentación

**Spec:** [`spec.md`](./spec.md) · **Plan:** [`plan.md`](./plan.md)
**Rama:** `feature/002-tipos-de-documentacion`
**Fecha:** 2026-11-03

Las incógnitas técnicas de la Fase 0, resueltas. Cada una lleva la decisión, por qué se
tomó y qué se descartó. Lo que aquí se decide es el *cómo*; el *qué* está en la spec.

---

## 1. ¿Interviene un modelo en el reconocimiento del formato?

**Decisión: la lectura es determinista y no interviene ningún modelo. Lo que no se reconozca
queda vacío, y el formato se acepta igual.**

> **Revisada dos veces.** El 2026-11-04 se cambió para que la IA propusiera la estructura cuando
> la lectura no reconociera nada (decisión 11). El **2026-11-05 esa revisión se revocó** y la
> decisión volvió a su forma original, porque lo que la motivaba desapareció: la IA entraba a
> rescatar los formatos que si no se rechazarían, y ahora no se rechaza ninguno.
>
> Lo que destrabó las dos revisiones fue entender **para qué** sirve la estructura: es la lista
> de qué preguntarle al RO (funcionalidad 004), no el documento que se entrega. El documento se
> escribe dentro del archivo original (RF-09), que se guarda intacto, así que el estilo del
> formato se conserva por construcción. Una estructura vacía no rompe nada: solo significa que
> la 004 tendrá que apoyarse en el archivo en vez de en una lista ya hecha.

**Por qué.** El Art. I dice que el sistema no agrega, quita, renombra ni reordena nada de la
estructura, y el Art. II que no completa ningún dato por su cuenta. Un modelo, por bueno que
sea, es una función que puede alucinar un nombre de columna o normalizar un título. Leer el
esqueleto de un `.docx` o un `.xlsx` con una librería es una operación cerrada: lo que sale
está en el archivo o no sale.

El Art. VI refuerza la conclusión desde la eficiencia: prohíbe mandar un Word o un Excel
completo a un modelo. Si el reconocimiento usara un modelo, habría que mandarle el documento
o un resumen de él, y un resumen ya es una interpretación.

**Consecuencia de alcance.** La 002 **no llega a LiteLLM ni a VORKAN por ningún camino**. Eso
deja el Art. V sin nada que regular aquí: no hay ningún modelo que elegir, ni en el código ni en
la configuración. El primer punto del módulo que habla con un modelo es la 004.

**Qué se descartó.** Que la IA reconociera **todos** los formatos, reemplazando la lectura
determinista. Es más uniforme —un solo camino que mantener— pero ninguna carga conservaría la
garantía de que lo reconocido sale del archivo y nada más, el techo de 30 s quedaría expuesto
en todas las cargas y no solo en las difíciles, y cada formato costaría tokens para resolver
algo que una librería resuelve gratis y sin equivocarse. Donde el archivo trae estilos de
título, la respuesta correcta ya está en el archivo: preguntarle a un modelo solo agrega una
forma de equivocarse.

## 2. ¿Con qué se lee la estructura de un `.docx`?

**Decisión: `python-docx`, leyendo los párrafos en orden y tomando como sección los que tienen
estilo de título (`Heading 1` … `Heading 9`, y sus equivalentes en español).**

> Esto dejó de ser un supuesto del plan: la aclaración del 2026-11-04 lo subió a la spec como
> **RF-05a**. Un párrafo en negrita no es una sección, y un Word sin estilos de título se
> rechaza con un mensaje que lo explica.

**Por qué.** `python-docx` da acceso al documento como secuencia de párrafos con su estilo, que
es exactamente el nivel que la spec pide: nombres de sección y su orden (RF-05). No hay que
interpretar el texto, solo recorrerlo.

El nivel del título (`1`, `2`, …) se guarda junto al nombre, porque la jerarquía es parte de la
estructura: una sección «Request» dentro de «Servicio» no es lo mismo que una «Request» de
primer nivel. Conservarla no es agregar información, es no perderla.

**Qué se descartó.**

- **MarkItDown.** La constitución lo nombra en el Art. VI, pero para los **insumos** que carga
  el RO, no para los formatos. MarkItDown convierte el documento a Markdown para que un modelo
  lo lea, y en el camino aplana lo que aquí importa: el orden exacto de las columnas de un
  Excel y la diferencia entre un título y un párrafo en negrita. Se usará en la 003, donde el
  objetivo sí es darle texto a un modelo.
- **Leer el XML del `.docx` a mano.** Un `.docx` es un ZIP con XML dentro y se puede recorrer sin
  dependencias. Funciona, pero habría que reimplementar la resolución de estilos heredados, que
  es donde está la complejidad real. No vale la pena.
- **Detectar secciones por heurística de formato** (tamaño de letra, negrita, numeración). Es
  adivinar, y choca con el Art. II.

## 3. ¿Con qué se lee la estructura de un `.xlsx`?

**Decisión: `openpyxl` en modo solo lectura, tomando las hojas en el orden del libro y, en cada
hoja, la primera fila con dos o más celdas con contenido como fila de encabezados.**

> También subió a la spec, como **RF-05b**, en la aclaración del 2026-11-04.

**Por qué.** `openpyxl` expone las hojas en orden y las celdas por coordenada, que es lo que la
spec pide para Excel: hojas con su orden, y columnas de cada hoja con nombre y orden (RF-05).
El modo solo lectura evita cargar el libro completo en memoria, que con el límite de 25 MB
importa.

La regla es explícita y verificable, no una heurística: muchos
formatos traen una fila de título o un logo arriba. Queda registrada en la estructura reconocida
—en qué fila se encontraron los encabezados— para que el Administrador pueda confirmarlo
mirando la pantalla (RF-08) y la decisión no sea invisible.

**Qué se descartó.**

- **`pandas.read_excel`.** Arrastra pandas entero por conveniencia, infiere tipos de dato que
  nadie pidió y renombra las columnas duplicadas (`Nombre`, `Nombre.1`), que es exactamente lo
  que el Art. I prohíbe. La spec dice que las columnas de nombre repetido se conservan todas, tal
  como vienen (sección 7).
- **Suponer que los encabezados están siempre en la fila 1.** Rechazaría formatos legítimos.

## 4. ¿Qué se valida antes de leer el archivo?

**Decisión: tres barreras en este orden —tamaño, extensión y firma del archivo— y solo después
se intenta leer.**

| Orden | Barrera | Qué rechaza |
|---|---|---|
| 1 | Tamaño máximo (25 MB por defecto, configurable) | Una carga accidental de algo que no es un formato, antes de gastar memoria en leerlo |
| 2 | Extensión en `.docx` / `.xlsx` | Los formatos no admitidos, incluidos `.doc` y `.xls` (RF-04) |
| 3 | Firma del archivo: los dos deben empezar por la firma ZIP (`PK\x03\x04`) | Un `.doc` renombrado a `.docx`, o cualquier archivo con la extensión cambiada |

**Por qué la tercera.** Los formatos actuales de Office son ZIP; los antiguos son binarios
propietarios. Confiar solo en la extensión dejaría entrar un archivo que la librería va a
rechazar más adelante con un error técnico, en vez del mensaje claro que pide RF-10. La firma se
lee de los primeros bytes, sin abrir el archivo.

**Nota sobre el orden:** el tamaño va primero a propósito. Verificar la extensión de un archivo
de 2 GB es gratis, pero recibirlo no: el límite se aplica mientras se recibe, no después.

## 5. ¿Dónde se guarda la estructura reconocida?

**Decisión: en una columna `JSONB` de la versión del formato, como un documento con listas
ordenadas.**

**Por qué.** La estructura se lee **siempre completa** —la pantalla de detalle la muestra entera,
la 004 y la 005 la recorren entera— y nunca se consulta por un campo suelto. Normalizarla en
tablas de secciones, hojas y columnas obligaría a reconstruir el orden en cada lectura con un
`ORDER BY`, y ahí es donde un error de implementación reordenaría la estructura sin que nadie lo
note. En una lista JSON el orden es el del documento y no hay nada que reconstruir.

`JSONB` y no `JSON` ni texto porque PostgreSQL lo valida al escribir: una estructura mal formada
falla al guardarse, no al leerse meses después.

**Qué se descartó.** El modelo relacional normalizado (`seccion`, `hoja`, `columna` con
`orden INTEGER`). Es la opción ortodoxa y permitiría consultas que nadie necesita, a cambio de
poner en riesgo lo único que el Art. I exige de verdad.

## 6. ¿Dónde se guarda el archivo original?

**Decisión: en el sistema de archivos, bajo una carpeta configurable (`VIDA_ALMACEN_FORMATOS`,
por defecto `uploads/formatos/`), con la ruta y el hash SHA-256 guardados en la base de datos.**

**Por qué.** El archivo se entrega completo o no se entrega (la 006 lo usa como plantilla del
documento final): no hay consulta parcial que justifique tenerlo en una columna. Un `BYTEA` de
hasta 25 MB por versión, multiplicado por los tipos y sus versiones, infla la base y cada copia
de seguridad con datos que no se consultan.

`uploads/` ya está en `.gitignore` desde la 001, así que la convención existe y ningún archivo
cargado puede llegar al repositorio por descuido (Art. X.2).

**El hash SHA-256** cumple dos funciones: detectar que el archivo en disco sigue siendo el que se
cargó, y dar un nombre de archivo que no depende del nombre que trajo el usuario —que puede
tener acentos, espacios o caracteres que el sistema de archivos no acepte—. El nombre original se
guarda en la base de datos como dato, no como ruta.

**Qué se descartó.**

- **`BYTEA` en PostgreSQL.** Más simple de respaldar como una unidad, y evita que la base y el
  disco se desincronicen. Es un empate razonable y conviene dejarlo anotado: si la 006 termina
  necesitando transacciones sobre el archivo, reconsiderarlo es barato porque la ruta está
  encapsulada en un solo módulo.
- **Un almacenamiento de objetos (S3 o equivalente).** Hoy no hay infraestructura para eso y
  agregaría credenciales que el Art. X.2 obliga a cuidar. La carpeta configurable deja la puerta
  abierta sin pagar nada ahora.

## 7. ¿Cómo se modela «una sola versión vigente»?

**Decisión: el tipo tiene una clave foránea a su versión vigente (`version_vigente_id`).**

**Por qué.** Reemplazar el formato es entonces una sola actualización de una fila: el tipo
apunta a la versión nueva. No existe el estado intermedio en el que dos versiones se declaran
vigentes, porque «vigente» no es un atributo de la versión sino una referencia del tipo.

**Qué se descartó.** Una columna `vigente BOOLEAN` en la versión, con un índice único parcial
(`WHERE vigente`). Funciona y PostgreSQL lo garantiza, pero el cambio son dos escrituras —apagar
la vieja, encender la nueva— y si la segunda falla el tipo queda sin ninguna versión vigente, es
decir, aparentemente incompleto.

## 8. ¿Cómo se evita que dos Administradores dejen el tipo a medias?

**Decisión: la carga completa ocurre en una transacción, que empieza tomando el candado de la
fila del tipo (`SELECT … FOR UPDATE`), y el archivo se escribe en disco **antes** de abrirla.**

**Por qué.** La spec exige que el tipo no quede con la estructura de un archivo y el archivo de
otro (sección 7). Tomar el candado del tipo serializa las dos cargas: la segunda espera y queda
como versión posterior. Y escribir el archivo primero —con su nombre derivado del hash, que no
colisiona— mantiene la transacción corta: dentro de ella solo hay inserciones, no entrada y
salida de disco.

Si la transacción falla después de escribir el archivo, queda un archivo huérfano en disco.
Es el lado correcto en el que fallar: sobra un archivo que nadie referencia, en vez de faltar
uno que la base dice que existe. La limpieza de huérfanos se puede agregar cuando se resuelva
el pendiente de retención del Art. X.4.

## 9. ¿Cómo se valida la generalización sin usar datos reales?

**Decisión: los formatos de prueba se **generan** con `python-docx` y `openpyxl` desde un
script del repositorio, con datos ficticios.**

**Por qué.** El Art. VIII pide validar con al menos un caso distinto al de referencia, y el
Art. X.3 que los casos de prueba usen solo datos ficticios. El caso de referencia real —el
Adapter Reverso— es un documento de un cliente: **no puede entrar al repositorio**. Lo que se
versiona es un Word ficticio que **imita su estructura** (sus secciones y su jerarquía), no su
contenido.

Generar los archivos en vez de cometerlos tiene dos ventajas: no hay binarios en el historial de
git, y la estructura esperada de cada caso queda escrita en código, al lado del archivo que la
produce, de modo que la prueba compara contra algo legible y no contra un valor mágico.

**Los tres casos:**

| Caso | Archivo | Para qué |
|---|---|---|
| Referencia | Word con la estructura del Adapter Reverso, contenido ficticio | Que el formato que el área usa hoy se reconozca bien |
| Generalización 1 | Word ficticio de otra forma (otra jerarquía, títulos repetidos, uno sin nombre) | Art. VIII, y los casos borde de la sección 7 |
| Generalización 2 | Excel ficticio (varias hojas, encabezados que no están en la fila 1, columnas repetidas) | Art. VIII en la rama de Excel |

**Qué se descartó.** Cometer una copia anonimizada del Adapter Reverso. Anonimizar un documento
es trabajo manual que se verifica mal, y un descuido pone datos de un cliente en un repositorio
de git, donde quedan para siempre. Imitar la estructura da el mismo valor de prueba sin ese
riesgo.

## 10. ¿Qué dependencias nuevas entran?

| Dependencia | Para qué | Por qué esa |
|---|---|---|
| `python-docx>=1.1` | Leer la estructura de `.docx` | Es la librería establecida para Word en Python; expone párrafos y estilos sin interpretar el contenido |
| `openpyxl>=3.1` | Leer la estructura de `.xlsx` | Estándar para Excel moderno; su modo solo lectura no carga el libro completo |

| `python-multipart>=0.0.20` | Leer el archivo de un `multipart/form-data` | Lo exige FastAPI para recibir un archivo; la carga del formato es el único punto de la plataforma que no es JSON |

**Ninguna llama a la red ni a un modelo**: la lectura del formato es local y cerrada. No entra
`pandas`, ni `markitdown`, ni un cliente HTTP de ejecución: `httpx` se queda como dependencia de
pruebas, que es donde la usa el `TestClient` de FastAPI.

## 11. ¿Qué pasa cuando la lectura no reconoce nada?

**Decisión: el formato se acepta igual, con la estructura vacía. Ningún modelo interviene en la
carga.**

**Por qué.** La lectura reconoce lo que Word marcó como título. Un formato que marque sus
secciones con negrita o con tamaño de letra es, para una persona, un documento con secciones;
para la librería, un archivo sin estructura. Durante un día esta decisión fue traer a la IA para
que propusiera la estructura en ese caso. La pregunta que lo cerró fue más simple: **¿por qué hay
que reconocer algo para poder subir el archivo?**

No hay que reconocerlo. El formato es la referencia con la que después se llena el documento, el
archivo original se guarda intacto y es ahí donde se escribe (RF-09). Lo que se reconozca al
cargar es una pista para que la 004 sepa por dónde empezar a preguntar; no reconocer nada deja a
la 004 con más trabajo, no a la plataforma sin funcionar.

**Qué desapareció al decidir eso.** El respaldo con IA existía por una sola razón: rescatar los
formatos que si no se rechazarían. Sin el rechazo se queda sin trabajo, y se fue completo —el
cliente de LiteLLM, el extractor del esqueleto, el descarte de RF-05d, sus cuatro variables de
entorno, su límite de espera y 380 líneas de pruebas—. La funcionalidad 002 no tiene ninguna
dependencia de LiteLLM.

**Lo que no cambió** es que la lectura sigue siendo determinista y sigue ocurriendo **una sola
vez, al cargar** (Art. VI). Lo reconocido se guarda con la versión, y ni el detalle del tipo ni
las funcionalidades posteriores vuelven a abrir el archivo para saber qué hay dentro.

**Qué se descartó.**

- **Una heurística propia sobre negritas y tamaños de letra**, sin IA. Es determinista, pero
  decide por su cuenta qué párrafo era un título, con reglas que nadie escribió en ninguna spec:
  inventa igual, solo que sin decirlo. Y ahora no hace falta: el formato se acepta de todas
  formas.
- **Pedirle a la IA que proponga la estructura al cargar** (la decisión del 2026-11-04). Se
  construyó, se probó y se quitó al día siguiente. Lo que la hacía necesaria era el rechazo, no
  la estructura.
- **Una compuerta de confirmación**: que la versión propuesta no quedara vigente hasta que el
  Administrador la aprobara. Se diseñó y se quitó el mismo día en que se construyó, por ser
  mucho aparato —estado en la base, ruta y pantalla— para proteger algo que no estaba en riesgo.
- **Rechazar también el archivo que no se puede abrir.** Eso **sí se conserva** (RF-10), y es el
  único rechazo que ocurre después de abrir el archivo. No es un juicio sobre su estructura: un
  `.docx` dañado o protegido con contraseña no lo va a poder llenar nadie, y descubrirlo al
  cargarlo es mucho más amable que descubrirlo cuando un RO ya documentó una actividad.
