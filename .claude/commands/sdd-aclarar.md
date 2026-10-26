---
description: Resuelve las aclaraciones pendientes de la spec de la rama actual
argument-hint: [respuestas opcionales del usuario]
---

Vas a resolver las aclaraciones abiertas de la especificación de la rama actual.

Información adicional del usuario (puede estar vacía):

$ARGUMENTS

Pasos:

1. Identifica la spec a partir del nombre de la rama actual (`git branch --show-current`, formato `feature/NNN-nombre`). Si no estás en una rama `feature/`, detente y avisa.
2. Lee `sdd/constitucion.md` y `specs/NNN-nombre/spec.md`.
3. Busca todas las marcas `[NECESITA ACLARACIÓN: ...]` y también ambigüedades no marcadas (términos vagos, criterios no verificables, contradicciones).
4. Si el usuario ya dio respuestas en los argumentos, aplícalas. Si no, hazle **una pregunta a la vez** (máximo 5 en total), con opciones concretas cuando sea posible, y espera la respuesta.
5. Actualiza la spec con cada respuesta y agrega al final una sección `## Registro de aclaraciones` con fecha, pregunta y respuesta.
6. Lo que el usuario no sepa responder queda como `PENDIENTE` con su nota; no lo completes por tu cuenta.
7. Commit: `spec(NNN): aclaraciones`.
8. Indica si la spec está lista para `/sdd-planificar`.
