# Checklist de [TIPO]: [NOMBRE DE LA FUNCIONALIDAD]

**Propósito:** [qué revisa esta checklist]
**Fecha:** [AAAA-MM-DD]
**Funcionalidad:** [enlace a `spec.md` o al documento que corresponda]

> La genera `/speckit-checklist` a partir del contexto y los requerimientos de la funcionalidad.
>
> **Quién la marca:** es un artefacto de revisión. Lo marca quien revisa, no quien construye
> (Art. VII: quien construye no se evalúa a sí mismo).
>
> **Qué significa `[x]`:** que el criterio de **calidad del requerimiento** se revisó y se
> cumple. No significa que la implementación esté terminada; eso lo dice `tasks.md`.

<!--
  ============================================================================
  Los ítems de abajo son EJEMPLOS, solo para ilustrar el formato.

  /speckit-checklist DEBE reemplazarlos por ítems reales, derivados de:
  - lo que pidió el usuario
  - los requerimientos de spec.md
  - el contexto técnico de plan.md
  - las tareas de tasks.md

  NO dejar estos ejemplos en la checklist generada.
  ============================================================================
-->

## [Categoría 1]

- [ ] CHK001 [primer criterio, con una acción clara]
- [ ] CHK002 [segundo criterio]
- [ ] CHK003 [tercer criterio]

## [Categoría 2]

- [ ] CHK004 [criterio de otra categoría]
- [ ] CHK005 [criterio con su medida concreta]

## Notas

- Marca `[x]` solo cuando la revisión confirme que el criterio se cumple.
- Deja sin marcar lo que todavía necesite aclaración, corrección o evaluación.
- `/speckit-implement` lee el estado de estas casillas como compuerta y no debe modificarlas.
- `checklists/requirements.md` tiene su propio ciclo de vida, que mantienen
  `/speckit-specify` y `/speckit-clarify`.
- Los hallazgos van escritos junto al ítem, no en otro archivo.
