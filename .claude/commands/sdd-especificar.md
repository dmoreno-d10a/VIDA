---
description: Crea una nueva especificación SDD con su rama y carpeta
argument-hint: <descripción en lenguaje natural de la funcionalidad o mejora>
---

Vas a crear una nueva **especificación** siguiendo el flujo SDD del proyecto.

Descripción entregada por el usuario:

$ARGUMENTS

Pasos:

1. Lee `sdd/constitucion.md` completo. Todo lo que escribas debe cumplirla.
2. **Antes de crear la rama, revisa si la funcionalidad ya tiene número reservado.** Lee `sdd/mapa-funcionalidades.md` y busca si lo que te pidió el usuario corresponde a una de las funcionalidades del mapa.
   - **Si está en el mapa:** usa el número que el mapa le reserva, pasándolo explícitamente. El mapa reserva números por funcionalidad y no las construimos en orden, así que el cálculo automático del script daría otro número y la carpeta dejaría de corresponder al mapa.
   - **Si no está en el mapa** (una mejora, una corrección, una funcionalidad nueva): no pases el número y deja que el script lo calcule.
   - Si tienes dudas de a qué funcionalidad del mapa corresponde, **pregúntale al usuario antes de crear la rama**. Una rama con el número equivocado hay que borrarla y repetir.
3. Propón un nombre corto en kebab-case (2 a 5 palabras, en español, sin tildes) para la funcionalidad y ejecuta una de estas dos:
   - Con número reservado: `SDD_NUMERO=NNN bash scripts/nueva-spec.sh <nombre-corto>`
   - Sin número reservado: `bash scripts/nueva-spec.sh <nombre-corto>`

   El script crea la rama `feature/NNN-<nombre-corto>` desde `main` y la carpeta `specs/NNN-<nombre-corto>/` con `spec.md` copiada de la plantilla. Si la rama ya existe porque alguien te la entregó creada, **no ejecutes el script**: trabaja sobre esa rama y sigue desde el paso siguiente.
4. Completa `specs/NNN-<nombre-corto>/spec.md` usando la estructura de `sdd/plantillas/spec.md`, sin agregar ni quitar secciones.
5. Reglas de redacción:
   - Describe **qué** y **por qué**. No menciones tecnologías, librerías, modelos, prompts ni estructura de código.
   - Si la funcionalidad involucra un formato de documentación, no inventes su estructura: pregunta al usuario o márcalo como aclaración.
   - No inventes datos de negocio. Todo lo que no esté claro va a la sección 9 como `[NECESITA ACLARACIÓN: ...]`. Usa como máximo 3 marcas; si hay más, prioriza las que afectan el alcance.
   - Cada criterio de aceptación debe poder verificarse (formato Dado / Cuando / Entonces).
6. Marca la checklist de la sección 10.
7. Haz commit: `spec(NNN): especificación inicial de <nombre-corto>`.
8. Responde en español con: ruta de la spec, rama creada, resumen en 3 líneas y la lista de aclaraciones pendientes. Si hay aclaraciones, pregunta al usuario antes de sugerir `/sdd-planificar`.
