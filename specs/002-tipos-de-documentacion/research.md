# Investigación: Tipos de documentación

**Spec:** [`spec.md`](./spec.md) · **Plan:** [`plan.md`](./plan.md)
**Rama:** `feature/002-tipos-de-documentacion`
**Fecha:** 2026-11-03

Las incógnitas técnicas de la Fase 0, resueltas. Cada una lleva la decisión, por qué se
tomó y qué se descartó. Lo que aquí se decide es el *cómo*; el *qué* está en la spec.

---

## 1. ¿Interviene un modelo en el reconocimiento del formato?

**Decisión: la lectura determinista es el camino principal; la IA solo entra como respaldo.**

> **Revisada el 2026-11-04.** La decisión original era que no interviniera ningún modelo. La
> aclaración de ese día la cambió: si la lectura determinista no reconoce nada, la IA propone la
> estructura (RF-05c). Lo que sigue explica por qué la lectura determinista conserva la
> prioridad; el respaldo está en la **decisión 11**.
>
> Lo que acotó el alcance de esa revisión fue entender **para qué** sirve la estructura: es la
> lista de qué preguntarle al RO (funcionalidad 004), no el documento que se entrega. El
> documento se escribe dentro del archivo original (RF-09), así que el estilo del formato se
> conserva por construcción y la estructura no tiene que ser una copia fiel del archivo: tiene
> que nombrar lo que hay que llenar.

**Por qué.** El Art. I dice que el sistema no agrega, quita, renombra ni reordena nada de la
estructura, y el Art. II que no completa ningún dato por su cuenta. Un modelo, por bueno que
sea, es una función que puede alucinar un nombre de columna o normalizar un título. Leer el
esqueleto de un `.docx` o un `.xlsx` con una librería es una operación cerrada: lo que sale
está en el archivo o no sale.

El Art. VI refuerza la conclusión desde la eficiencia: prohíbe mandar un Word o un Excel
completo a un modelo. Si el reconocimiento usara un modelo, habría que mandarle el documento
o un resumen de él, y un resumen ya es una interpretación.

**Consecuencia de alcance.** La 002 **sí llega a LiteLLM y VORKAN**, pero solo por el camino de
respaldo. Eso hace que el Art. V vuelva a aplicar: el modelo no puede quedar escrito en el
código. Su configuración es parte de los parámetros del sistema (funcionalidad 007), así que
aquí entra como variable de entorno con valor por defecto, no como una pantalla nueva.

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
hoja, la primera fila no vacía como fila de encabezados.**

> También subió a la spec, como **RF-05b**, en la aclaración del 2026-11-04.

**Por qué.** `openpyxl` expone las hojas en orden y las celdas por coordenada, que es lo que la
spec pide para Excel: hojas con su orden, y columnas de cada hoja con nombre y orden (RF-05).
El modo solo lectura evita cargar el libro completo en memoria, que con el límite de 25 MB
importa.

«La primera fila no vacía» es una regla explícita y verificable, no una heurística: muchos
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

| `httpx>=0.28` | Hablar con LiteLLM en el paso de respaldo | Ya está en el proyecto como dependencia de pruebas de la 001; solo sube a dependencia de ejecución |

Ninguna de las dos primeras llama a la red ni a un modelo: la lectura del formato sigue siendo
local y cerrada. No entra `pandas`, ni `markitdown`, ni un SDK de proveedor —LiteLLM se habla
por HTTP, que es lo que lo hace intercambiable (Art. V, decisión 11).

## 11. ¿Cómo entra la IA cuando la lectura determinista no reconoce nada?

**Decisión: un paso de respaldo que propone la estructura, con dos cercos: se le manda texto y
no el archivo, y se descarta lo que no esté en el documento.**

**Por qué hace falta.** La lectura determinista reconoce lo que Word marcó como título. Un
formato que marque sus secciones con negrita o con tamaño de letra es, para una persona, un
documento con secciones; para la librería, un archivo sin estructura. Rechazarlo era el
comportamiento correcto mientras no hubiera alternativa, pero si esa es la convención del área,
la plataforma no serviría para los formatos que existen (era el riesgo CHK030 de la checklist).

**Los dos cercos**, que son lo que hace que esto no contradiga los artículos I y II:

1. **No se le manda el archivo, se le manda texto.** Del `.docx` se extraen los párrafos con sus
   señales de forma —negrita, tamaño, si está solo en su línea— y del `.xlsx` los nombres de las
   hojas y sus primeras filas. Eso respeta el Art. VI, que prohíbe mandar el documento completo,
   y mantiene el costo acotado al esqueleto en vez del contenido.
2. **Se descarta lo que no esté en el documento.** Cada nombre que la IA proponga se busca
   literalmente en el texto extraído; el que no aparezca no entra (RF-05d). Es una verificación
   mecánica, no una confianza: convierte el criterio CE-04 en algo que una prueba puede afirmar.

**El modelo no queda en el código** (Art. V): se configura por variable de entorno, con la
dirección de LiteLLM y el nombre de la tarea. El respaldo además **se puede apagar**: con
`VIDA_IA_RESPALDO=0` la funcionalidad se comporta como el diseño original y rechaza el formato,
lo que sirve para las pruebas y para un despliegue sin acceso a VORKAN.

**Qué se descartó.**

- **Una heurística propia sobre negritas y tamaños de letra**, sin IA. Es determinista, pero
  decide por su cuenta qué párrafo era un título, con reglas que nadie escribió en ninguna spec:
  inventa igual, solo que sin decirlo.
- **Una compuerta de confirmación**: que la versión propuesta no quedara vigente hasta que el
  Administrador la aprobara. Se diseñó así y se quitó el mismo día. El argumento para quitarla:
  lo que la estructura decide es qué se le pregunta al RO, y una lista mal reconocida se nota al
  abrir una actividad y se corrige recargando el archivo, sin que ningún documento entregado
  quede mal. Una compuerta con su estado en la base, su ruta y su pantalla era mucho aparato para
  proteger algo que no estaba en riesgo. El Administrador revisa la estructura en el detalle del
  tipo (RF-08), que ya existía.
- **Resolver el respaldo en segundo plano.** Separaría esta carga del techo de 30 s, pero la
  aclaración del 2026-11-04 fijó que todo se resuelve en la misma petición; el respaldo trabaja
  sobre texto, así que cabe.
