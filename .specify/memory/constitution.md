# Constitución de V.I.D.A.

*Vortexbird Intelligent Documentation Assistant*

**Versión:** 1.0.0
**Fecha de ratificación:** 2026-10-25
**Responsable del proyecto:** Diego Moreno (Requirements Owner)

Esta constitución reúne los principios no negociables del proyecto. Toda especificación, plan, tarea e implementación debe cumplirlos. Si algo entra en conflicto con un artículo, prevalece la constitución, y el conflicto se resuelve enmendándola (ver *Gobernanza*), nunca ignorándola.

---

## Propósito

V.I.D.A. es una plataforma web que apoya a los Requirements Owners (RO) de VortexBird en sus tareas recurrentes. Su primer módulo genera la documentación técnica que se entrega a las fábricas de desarrollo. La plataforma debe permitir agregar nuevos módulos (por ejemplo, pruebas de carga o análisis de APIs) sin rehacer lo existente.

## Artículo I — El formato definido manda

La estructura de cada documento (secciones, hojas, columnas, orden y nombres) la define el formato que cargó el administrador. El sistema no agrega, quita, renombra ni reordena nada de esa estructura.

## Artículo II — Cero información inventada

El sistema solo usa lo que el RO cargó o respondió. Ningún modelo completa un dato por su cuenta, aunque parezca obvio.

## Artículo III — El RO decide

Cuando falta información, el sistema pregunta. El RO responde o elige dejarlo pendiente. Lo que quede pendiente aparece en el documento generado como `PENDIENTE`. Un documento con pendientes es válido; uno con datos inventados no lo es.

## Artículo IV — Separación de capas

El front no contiene lógica de IA ni credenciales. Toda la lógica de análisis, preguntas y generación vive aparte, y el acceso a modelos se hace únicamente a través de **LiteLLM** hacia **VORKAN**.

## Artículo V — Independencia del modelo

El modelo que usa cada tarea es configuración. Cambiar de modelo no requiere cambiar código ni lógica.

## Artículo VI — Eficiencia de tokens

Ningún archivo Word o Excel se envía tal cual a un modelo. Los insumos se convierten a Markdown (MarkItDown), los formatos se analizan una sola vez al cargarse, y a cada llamada solo se envía la información necesaria.

## Artículo VII — Quien construye no se evalúa a sí mismo

La generación y la verificación de calidad las hacen agentes independientes desde la primera versión. El documento se califica con una rúbrica medible. Los criterios, pesos, puntaje mínimo e iteraciones máximas son parámetros editables, no valores fijos en el código. Si el documento no alcanza el mínimo dentro de las iteraciones permitidas, pasa a revisión humana.

## Artículo VIII — Generalización

V.I.D.A. debe funcionar con cualquier formato que cargue el administrador, no solo con el caso de referencia (Adapter Reverso). Cada capacidad se valida con al menos un caso distinto al de referencia.

## Artículo IX — Trazabilidad

Cada campo del documento generado debe poder rastrearse a su origen: archivo cargado, texto ingresado, respuesta del RO o pendiente.

## Artículo X — Seguridad y datos

1. Solo usuarios autenticados, con dos roles: **RO** y **Administrador**.
2. Ningún secreto, key o credencial en el código ni en el repositorio.
3. Los casos de prueba del repositorio usan solo datos ficticios.
4. **PENDIENTE:** tiempo de retención y eliminación de los archivos que cargan los RO.
5. **PENDIENTE:** política sobre qué información puede enviarse a modelos gratuitos a través del Vorkan Gateway.

## Artículo XI — Spec antes que código

Cada funcionalidad sigue el flujo **Especificación → Planificación → Tareas → Implementación**, en su propia rama `feature/NNN-nombre`. No se implementa nada que no esté en las tareas aprobadas. Una spec describe **qué** y **por qué**; el **cómo** pertenece al plan.

## Artículo XII — Idioma

La plataforma, la documentación del proyecto y los documentos generados están en español.

---

## Gobernanza

- Esta constitución solo se modifica mediante un **Pull Request dedicado** (rama `constitucion/vX.Y.Z`). No se admiten cambios directos sobre `main`.
- El PR requiere la aprobación del responsable del proyecto.
- Versionado:
  - **MAJOR:** se elimina un artículo o se cambia su sentido.
  - **MINOR:** se agrega un artículo o se amplía uno existente.
  - **PATCH:** redacción, ortografía o aclaraciones sin cambio de sentido.
- Cada plan (`plan.md`) incluye una verificación explícita contra esta constitución.

## Registro de enmiendas

| Versión | Fecha | Autor | Cambio |
|---|---|---|---|
| 1.0.0 | 2026-10-25 | Diego Moreno | Ratificación inicial |
