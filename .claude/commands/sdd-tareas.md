---
description: Descompone el plan de la rama actual en tareas verificables
---

Vas a generar la lista de **tareas** de la especificación de la rama actual.

Pasos:

1. Identifica la spec por la rama actual (`feature/NNN-nombre`). Si no estás en una rama `feature/`, detente y avisa.
2. Lee `sdd/constitucion.md`, `specs/NNN-nombre/spec.md` y `specs/NNN-nombre/plan.md`. Si no existe `plan.md`, detente y sugiere `/sdd-planificar`.
3. Crea `specs/NNN-nombre/tareas.md` con la estructura de `sdd/plantillas/tareas.md`.
4. Reglas:
   - Numera las tareas de forma consecutiva: T001, T002, ...
   - Cada tarea debe poder completarse en una sesión de trabajo y tener un criterio de terminado verificable.
   - Cada tarea indica qué RF o HU cubre. Ningún RF de la spec puede quedar sin tarea.
   - Los casos de prueba y su respuesta esperada se definen **antes** de construir (Fase 2).
   - Marca con `[P]` solo las tareas que no tocan los mismos archivos ni dependen entre sí.
5. Al final del archivo agrega una tabla de cobertura: `RF / HU → tareas`.
6. Commit: `tareas(NNN): descomposición en tareas`.
7. Responde con el número de tareas por fase y sugiere `/sdd-implementar`.
