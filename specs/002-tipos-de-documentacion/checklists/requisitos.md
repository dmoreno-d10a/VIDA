# Checklist de calidad de requerimientos: Tipos de documentación

**Propósito:** revisar si los requerimientos de la spec 002 están completos, son claros, no se
contradicen y pueden verificarse. **No revisa la implementación**: revisa lo que la spec dice y
lo que no dice.
**Fecha:** 2026-11-04
**Funcionalidad:** [`../spec.md`](../spec.md)

> La genera `/speckit-checklist` a partir del contexto y los requerimientos de la funcionalidad.
>
> **Quién la marca:** es un artefacto de revisión. Lo marca quien revisa, no quien construye
> (Art. VII: quien construye no se evalúa a sí mismo). Por eso llega **toda sin marcar**.
>
> **Qué significa `[x]`:** que el criterio de **calidad del requerimiento** se revisó y se
> cumple. No significa que la implementación esté terminada; eso lo dice `tasks.md`.
>
> **Compuerta de PR:** `CONTRIBUTING.md` exige la revisión de otro integrante del área RO. Esta
> checklist es el guion de esa revisión, no una lista de cortesía.

---

## Completitud de los requerimientos

- [ ] CHK001 ¿Están definidos los límites de longitud del nombre y la descripción de un tipo? El RF-02 exige que el nombre sea único, pero no dice cuánto puede medir ninguno de los dos [Vacío, Spec §4 RF-02]
- [ ] CHK002 ¿Está especificado qué pasa si el almacén de archivos no se puede escribir —disco lleno, carpeta sin permisos, ruta mal configurada—? Es una falla distinta de las del RF-10, que son todas del archivo [Vacío, Spec §7]
- [ ] CHK003 ¿Dice la spec si el Administrador puede consultar la estructura de un tipo **desactivado**? El RF-14 dice que sigue visible para él, pero no si eso incluye su estructura y su historial [Vacío, Spec §4 RF-14]
- [ ] CHK004 ¿Está definido si el RO ve algo del formato además del nombre y la descripción —por ejemplo, si el tipo es Word o Excel—? La 003 podría necesitarlo para decidir qué le pide al RO [Vacío, Spec §4 RF-16]
- [ ] CHK005 ¿Está escrito en la spec que las versiones anteriores se conservan **indefinidamente**? Hoy solo aparece como consecuencia del RF-19 y como mención en el pendiente del Art. X.4 [Completitud, Spec §10]
- [ ] CHK006 ¿Hay un requerimiento sobre qué se hace con un archivo que quedó en el almacén sin versión que lo referencie? El plan lo trata como aceptable, pero la spec no lo menciona [Vacío, Recuperación]
- [ ] CHK007 ¿Están definidos los requerimientos de registro y diagnóstico? Si meses después un documento sale mal, ¿qué queda escrito para saber qué estructura se reconoció y cuándo? [Vacío, No funcional]

## Claridad de los requerimientos

- [ ] CHK008 El RF-05a dice que el estilo de título se reconoce «por la marca que Word guarda dentro del archivo, que es la misma en cualquier idioma». ¿Es esa una afirmación verificable tal como está escrita, o deja al implementador decidir qué marca es? [Claridad, Spec §4 RF-05a]
- [ ] CHK009 ¿Distingue la spec entre las tres causas de rechazo del RF-10 —dañado, protegido con contraseña, sin estructura reconocible— o las trata como una sola? El contrato de la API usa dos mensajes distintos, así que la spec debería decidirlo [Claridad, Spec §4 RF-10]
- [ ] CHK010 ¿Está claro qué significa «primera fila con contenido» cuando la fila tiene una sola celda escrita y el resto vacías? El RF-05b fija la regla pero no el umbral [Ambigüedad, Spec §4 RF-05b]
- [ ] CHK011 ¿Define la spec qué es un nombre de tipo válido? El contrato rechaza un nombre que queda vacío al quitar espacios, pero esa regla no está en ningún RF [Claridad, Spec §4 RF-02]
- [ ] CHK012 ¿Está definido si la comparación de nombres repetidos distingue mayúsculas y acentos? El modelo de datos decide comparar en minúsculas y sin espacios de sobra, lo que es una regla de negocio, no de implementación [Ambigüedad, Spec §4 RF-02]

## Consistencia de los requerimientos

- [ ] CHK013 El RF-04 habla de «**un** archivo de formato vigente» y el RF-19 de versionado. ¿Queda claro que no se contradicen, y que la sección 8 lo cierra al excluir varios formatos vigentes a la vez? [Consistencia, Spec §4 RF-04, RF-19]
- [ ] CHK014 La sección 8 excluye el **registro de auditoría** de quién creó o cambió cada tipo. Pero el RF-20 y el RF-21 guardan la fecha de cada versión y la muestran. ¿Es una contradicción, o la frontera entre «historial del formato» y «auditoría de usuarios» está suficientemente dicha? [Conflicto, Spec §8, §4 RF-21]
- [ ] CHK015 ¿Conviven sin contradicción el criterio de aceptación de HU-4 sobre «un tipo que ya fue usado por algún RO» y el RF-15a, que hoy define «usado» como «con formato vigente»? [Consistencia, Spec §3 HU-4, §4 RF-15a]
- [ ] CHK016 ¿Es consistente el término usado para el mismo concepto a lo largo de la spec: «formato», «versión del formato», «estructura reconocida» y «archivo original»? Un mismo nombre para dos cosas distintas es lo que después produce código equivocado [Terminología]
- [ ] CHK017 El RF-03 define tres estados. ¿Está dicho en la spec que **no existe** la transición de `activo` a `incompleto`, es decir, que a un tipo no se le puede quitar el formato? El modelo de datos lo asume [Consistencia, Spec §4 RF-03]

## Calidad de los criterios de aceptación

- [ ] CHK018 Los criterios de éxito de la sección 9 están numerados `CE-01` a `CE-10`, y las tareas los citan por ese identificador. ¿Queda cada criterio trazable desde una tarea y desde el PR, sin ambigüedad y sin que ninguno quede sin tarea? [Trazabilidad, Spec §9]
- [ ] CHK019 El techo de **30 segundos**, ¿dice dónde se mide? No es lo mismo el tiempo de proceso en el servidor que el tiempo de punta a punta incluyendo la subida del archivo por la red, y con 25 MB la diferencia es grande [Medibilidad, Spec §9]
- [ ] CHK020 «**1 sola vez** se analiza cada formato», ¿cómo se verifica objetivamente? Es un criterio sobre algo que no se ve desde afuera [Medibilidad, Spec §9]
- [ ] CHK021 «**0 elementos inventados**», ¿está definido contra qué se compara para poder afirmarlo? La estrategia de validación lo responde con los formatos generados, pero el criterio por sí solo no dice la referencia [Medibilidad, Spec §9]
- [ ] CHK022 ¿Son todos los criterios de aceptación de las cinco historias verificables en formato Dado/Cuando/Entonces, sin ninguno que dependa de un juicio de valor? [Calidad de criterios, Spec §3]

## Cobertura de escenarios

- [ ] CHK023 ¿Están cubiertos los cinco tipos de escenario —principal, alterno, de excepción, de recuperación y no funcional— o alguno falta sin que se diga que se excluye a propósito? El de **recuperación** es el que se ve más flojo [Cobertura]
- [ ] CHK024 ¿Hay requerimientos para el estado vacío de la pantalla del Administrador, cuando todavía no existe ningún tipo? La HU-5 cubre el caso del RO, pero no el del Administrador [Vacío, Cobertura]
- [ ] CHK025 ¿Está cubierto qué ve el Administrador **mientras** se analiza un formato que tarda? Con un techo de 30 s, la espera es parte de la experiencia [Vacío, Cobertura]
- [ ] CHK026 ¿Están definidos los requerimientos de accesibilidad de las dos pantallas nuevas? Ni esta spec ni la 001 los mencionan; conviene decidir si se excluyen a propósito o es un olvido [Vacío, No funcional]

## Cobertura de casos borde

- [ ] CHK027 ¿Hay un límite para el tamaño de la estructura reconocida: cuántas secciones, hojas o columnas puede traer un formato? Un archivo de 25 MB podría traer miles [Vacío, Caso borde]
- [ ] CHK028 ¿Está definido el caso de un nombre de sección o de columna extremadamente largo, o con caracteres que no se puedan mostrar? [Vacío, Caso borde]
- [ ] CHK029 ¿Están cubiertos en los requerimientos los casos borde de la sección 7 que hoy solo viven como viñetas, sin un RF que los respalde: nombres repetidos, elementos sin nombre, carga simultánea? [Cobertura, Spec §7]

## Supuestos y dependencias

- [ ] CHK030 El RF-05a suponía que los formatos Word del área marcan sus secciones con **estilos de título**, y ese era el supuesto que podía invalidar la funcionalidad. Dejó de poder hacerlo porque un formato ya no se rechaza por su estructura (RF-05c, RF-10). ¿Queda algún requerimiento que siga dependiendo del supuesto original? [Supuesto, Spec §4 RF-05a, RF-05c]
- [ ] CHK031 ¿Está documentado el supuesto de que la carpeta del almacén es persistente y se respalda? Si se pierde, quedan versiones en la base sin archivo, y la 006 no podría generar nada [Supuesto, Spec §4 RF-09]
- [ ] CHK032 ¿Está declarada la dependencia de la funcionalidad 001 —autenticación y los dos roles— y qué pasaría si sus reglas cambiaran? [Dependencia, Spec §2]
- [ ] CHK033 La 002 depende de un modelo **solo** por el camino de respaldo. ¿Está dicho en la spec con esa precisión —qué parte no lo usa nunca y qué parte sí—, o hay que deducirlo del plan? [Claridad, Spec §4 RF-05c]

## Verificación contra la constitución

- [ ] CHK034 **Art. I** — ¿Hay algún requerimiento que permita al sistema alterar la estructura del formato: completar, normalizar, ordenar o deduplicar? Buscar lo que *autoriza*, no solo lo que prohíbe [Consistencia constitucional]
- [ ] CHK035 **Art. II** — ¿Queda algún punto donde el sistema tenga que elegir entre dos interpretaciones de un archivo? Cada uno de esos puntos es una oportunidad de inventar, y debería estar resuelto por una regla explícita [Consistencia constitucional, Spec §4 RF-05a, RF-05b]
- [ ] CHK036 **Art. VIII** — ¿Garantizan los requerimientos que ningún nombre de sección, hoja o columna quede escrito en la plataforma? El RF-17 lo exige; ¿hay algo en el resto de la spec que lo contradiga? [Consistencia constitucional, Spec §4 RF-17]
- [ ] CHK037 **Art. IX** — ¿Alcanza lo que guarda el RF-20 para rastrear un campo de un documento generado hasta su origen, o falta algo que las funcionalidades 005 y 006 vayan a necesitar? [Completitud constitucional, Spec §4 RF-20]
- [ ] CHK038 **Art. X.3** — ¿Está dicho en la spec que los casos de prueba usan solo datos ficticios, y que el formato real del cliente no entra al repositorio? Hoy esa decisión vive en `research.md`, que es plan [Completitud constitucional, Spec §9]

## Aceptar el formato sin evaluarlo (RF-05c, RF-10)

> Reescritos el 2026-11-05. Los siete ítems anteriores preguntaban por el respaldo con IA, que se
> quitó ese día junto con el rechazo que lo justificaba. Estos preguntan por lo que quedó, que es
> más simple pero no por eso está bien dicho.

- [ ] CHK039 El RF-05c dice que un formato del que no se reconoce nada se acepta con la estructura vacía. ¿Está dicho **qué hace la 004** con una estructura vacía? Si no se ha pensado, el formato se acepta y el problema reaparece más adelante, cuando un RO ya eligió ese tipo [Vacío, Spec §4 RF-05c]
- [ ] CHK040 ¿Está definido qué significa «no se reconoció nada» de forma que se pueda verificar? En Word es «ninguna sección», y en Excel la spec dice «ninguna hoja con al menos una columna»: ¿es esa la regla que el negocio quiere para un libro con diez hojas de las que solo una trae encabezados? [Medibilidad, Spec §4 RF-05c]
- [ ] CHK041 El RF-10 conserva el rechazo del archivo que **no se puede abrir** —dañado o protegido con contraseña—. ¿Es consistente rechazar ese y aceptar uno sin estructura? El argumento es que el primero no lo puede llenar nadie: ¿está ese argumento en la spec o solo en el código? [Consistencia, Spec §4 RF-10]
- [ ] CHK042 Ahora que el tipo queda activo pase lo que pase con su estructura, **la revisión del Administrador no cambia nada**: no hay nada que aprobar ni rechazar. ¿Sigue teniendo sentido la pantalla de detalle como «revisión» (RF-08), o es solo información? Si es solo información, conviene que la spec lo diga así y no prometa una revisión que no tiene efecto [Claridad, Spec §4 RF-08]
- [ ] CHK043 ¿Está dicho qué ve un RO cuando elige un tipo cuyo formato no tiene estructura reconocida? Para él el tipo está activo y se ve igual que cualquier otro; la diferencia aparece en la 004. Si eso no está previsto, el costo de aceptar todo lo paga él [Vacío, Spec §4 RF-16, RF-05c]
- [ ] CHK044 ¿Está dicho en la spec que la estructura reconocida sirve para **saber qué preguntarle al RO**, y que el documento final se escribe dentro del archivo original en vez de reconstruirse? Es lo que explica por qué el estilo del formato no corre riesgo, y por qué una estructura vacía no rompe nada [Claridad, Spec §4 RF-05, RF-09]

## Notas

- Marca `[x]` solo cuando la revisión confirme que el criterio se cumple.
- Deja sin marcar lo que todavía necesite aclaración, corrección o evaluación.
- `/speckit-implement` lee el estado de estas casillas como compuerta y no debe modificarlas.
- `checklists/requirements.md` tiene su propio ciclo de vida, que mantienen
  `/speckit-specify` y `/speckit-clarify`.
- Los hallazgos van escritos junto al ítem, no en otro archivo.

**Por dónde empezar:** CHK039 y CHK043. Los dos preguntan lo mismo desde dos lados: aceptar
cualquier formato le quita el problema al Administrador, pero **no lo resuelve**, y hay que
decidir dónde reaparece. Si la respuesta es «la 004 se las arregla», conviene escribirlo antes de
especificar la 004 y no después. CHK030, que era el ítem que podía invalidar la funcionalidad,
dejó de serlo.
