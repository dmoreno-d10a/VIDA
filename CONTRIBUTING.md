# Guía de contribución

## Ramas

| Rama | Uso | Se crea desde | Se integra en |
|---|---|---|---|
| `main` | Versión estable. Nadie hace commit directo. | — | — |
| `feature/NNN-nombre` | Una especificación (funcionalidad o mejora). | `main` | `main` vía PR |
| `fix/NNN-descripcion` | Corrección sobre una spec ya integrada. `NNN` es la spec que se corrige. | `main` | `main` vía PR |
| `constitucion/vX.Y.Z` | Enmienda a la constitución. | `main` | `main` vía PR |

- Las ramas `feature/` se crean **solo** con `bash scripts/nueva-spec.sh <nombre>` o con `/sdd-especificar`, para que la numeración no se repita.
- Antes de abrir el PR, actualiza tu rama con `main` (`git pull --rebase origin main`).
- Una rama se elimina después de integrarse.

## Commits

Formato: `<tipo>(<spec>): <descripción en minúscula>`

| Tipo | Cuándo |
|---|---|
| `spec(NNN)` | Crear o ajustar la especificación |
| `plan(NNN)` | Crear o ajustar el plan |
| `tareas(NNN)` | Crear o ajustar las tareas |
| `TNNN` | Implementación de una tarea (ej. `T004: agrega lector de hoja Request`) |
| `constitucion` | Enmienda (`constitucion: v1.1.0 - agrega artículo de auditoría`) |
| `docs` / `chore` | Documentación general o mantenimiento |

## Pull Request hacia `main`

Título: `[NNN] Nombre de la especificación`

Checklist obligatoria en la descripción del PR:

```markdown
- [ ] La spec no tiene marcas [NECESITA ACLARACIÓN] abiertas que afecten el alcance
- [ ] plan.md incluye la verificación contra la constitución
- [ ] Todas las tareas de tareas.md están en [x]
- [ ] Se validó con el caso de referencia y con al menos un caso distinto
- [ ] Sin secretos, keys ni datos reales de clientes en el diff
- [ ] Documentación actualizada
```

**Aprobación:** mínimo una revisión de otro integrante del área RO. Las enmiendas a la constitución solo entran por Pull Request y requieren aprobación del responsable del proyecto.

## Qué nunca se sube

- Archivos `.env`, keys, tokens, credenciales o cookies.
- Documentos con datos reales de clientes, cuentas o personas.
- Archivos cargados por los RO o documentos generados con datos reales.
