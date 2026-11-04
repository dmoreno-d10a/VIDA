# Especificaciones

Una carpeta por especificación, creada con `/speckit-specify`.

```
specs/NNN-nombre/
├── spec.md            # qué y por qué
├── plan.md            # cómo
├── tasks.md           # pasos verificables
├── research.md        # decisiones técnicas resueltas (si el plan tenía incógnitas)
├── data-model.md      # entidades y relaciones (si maneja datos)
├── quickstart.md      # cómo levantarlo y probarlo en local
├── contracts/         # contratos de interfaces o endpoints (si expone alguna)
└── checklists/        # revisiones de calidad de los requerimientos
```

Los cuatro últimos los genera `/speckit-plan` o `/speckit-checklist`, y solo cuando aplican.
Todos se escriben en español (Art. XII).

| # | Especificación | Rama | Estado |
|---|---|---|---|
| 001 | [Acceso y roles](001-acceso-y-roles/spec.md) | — (integrada) | Hecha |
| 002 | Tipos de documentación | `feature/002-tipos-de-documentacion` | Spec en curso (vive en su rama) |
