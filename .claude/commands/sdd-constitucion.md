---
description: Propone una enmienda a la constitución del proyecto
argument-hint: <cambio que se quiere hacer a la constitución>
---

Vas a proponer una **enmienda** a `sdd/constitucion.md`.

Cambio solicitado:

$ARGUMENTS

Pasos:

1. Lee `sdd/constitucion.md` completo.
2. Determina el tipo de cambio según la sección *Gobernanza* (MAJOR, MINOR o PATCH) y calcula la nueva versión.
3. Crea la rama `constitucion/vX.Y.Z` desde `main`.
4. Aplica el cambio, actualiza el encabezado de versión y agrega una fila al *Registro de enmiendas*.
5. Revisa si el cambio afecta specs o planes existentes en `specs/` y lista cuáles deberían revisarse.
6. Commit: `constitucion: vX.Y.Z - descripción`.
7. Responde con el resumen del cambio, la nueva versión y las specs afectadas. Recuerda que la enmienda requiere aprobación del responsable del proyecto vía Pull Request.
