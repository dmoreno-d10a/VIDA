---
description: Genera el plan técnico de la spec de la rama actual
argument-hint: [indicaciones técnicas opcionales: modelos, herramientas, restricciones]
---

Vas a crear el **plan técnico** de la especificación de la rama actual.

Indicaciones técnicas del usuario (pueden estar vacías):

$ARGUMENTS

Pasos:

1. Identifica la spec por la rama actual (`feature/NNN-nombre`). Si no estás en una rama `feature/`, detente y avisa.
2. Lee `sdd/constitucion.md`, `specs/NNN-nombre/spec.md` y los `plan.md` de specs ya integradas que tengan relación.
3. Si la spec tiene marcas `[NECESITA ACLARACIÓN]` que afectan el alcance, detente y sugiere `/sdd-aclarar`.
4. Crea `specs/NNN-nombre/plan.md` con la estructura de `sdd/plantillas/plan.md`, sin agregar ni quitar secciones.
5. Reglas:
   - Completa primero la sección 2 (verificación contra la constitución). Si un artículo no se cumple, detente y explícale al usuario por qué antes de seguir.
   - Cada componente debe indicar qué RF o HU cubre. Nada en el plan sin respaldo en la spec.
   - Los modelos de IA se definen como configuración (Art. V) y solo se accede a ellos vía LiteLLM (Art. IV).
   - Prefiere la solución más simple que cumpla la spec.
6. Si necesitas investigar algo (formato de archivos, librerías), deja las conclusiones en `specs/NNN-nombre/investigacion.md`.
7. Commit: `plan(NNN): plan técnico`.
8. Responde con un resumen del enfoque, los riesgos principales y sugiere `/sdd-tareas`.
