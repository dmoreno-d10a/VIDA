---
description: Implementa las tareas pendientes de la spec de la rama actual
argument-hint: [ID de tarea o rango opcional, ej. T004 o T004-T008]
---

Vas a **implementar** tareas de la especificación de la rama actual.

Alcance pedido por el usuario (si está vacío, toma la siguiente tarea pendiente):

$ARGUMENTS

Pasos:

1. Identifica la spec por la rama actual (`feature/NNN-nombre`). Si no estás en una rama `feature/`, detente y avisa.
2. Lee `sdd/constitucion.md`, `spec.md`, `plan.md` y `tareas.md` de la carpeta de la spec.
3. Por cada tarea en el alcance, en orden:
   a. Implementa solo lo que la tarea describe. Si descubres que falta algo en la spec o el plan, **detente**, explícalo y propone el ajuste; no lo implementes por tu cuenta.
   b. Verifica el criterio de terminado (ejecuta pruebas o scripts si aplica).
   c. Marca la tarea con `[x]` en `tareas.md`.
   d. Haz commit: `TNNN: descripción corta`.
4. Reglas que no se negocian:
   - Ningún secreto, key o token en archivos del repo (Art. X).
   - Ningún dato real de clientes en casos de prueba (Art. X).
   - El front no contiene lógica de IA ni credenciales (Art. IV).
   - Los modelos de IA solo se referencian desde configuración (Art. V).
5. Al terminar, responde con: tareas completadas, tareas pendientes y cualquier bloqueo. Si ya no quedan tareas, sugiere abrir el Pull Request hacia `main` con la checklist de `CONTRIBUTING.md`.
