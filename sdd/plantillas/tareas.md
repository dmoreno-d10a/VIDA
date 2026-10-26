# Tareas: [NOMBRE DE LA FUNCIONALIDAD]

**Spec:** [`spec.md`](./spec.md) · **Plan:** [`plan.md`](./plan.md)
**Rama:** `feature/[NNN-nombre-corto]`

> Reglas:
> - Cada tarea es pequeña, verificable y tiene un criterio de terminado.
> - `[P]` indica que la tarea puede hacerse en paralelo con otras `[P]` de la misma fase.
> - Se marca `[x]` solo cuando el criterio de terminado se cumple.
> - Un commit por tarea, con el ID en el mensaje: `T003: descripción`.

---

## Fase 1 — Preparación

- [ ] **T001** [descripción]
  - Terminado cuando: [criterio verificable]
  - Cubre: [RF-XX / HU-X]

## Fase 2 — Casos de prueba primero

- [ ] **T00X** [P] Definir la respuesta esperada del caso de referencia
  - Terminado cuando: existe la respuesta esperada del caso, en la ruta definida en el plan
- [ ] **T00X** [P] Definir la respuesta esperada del caso de generalización
  - Terminado cuando: ...

## Fase 3 — Construcción

- [ ] **T00X** [descripción]
  - Terminado cuando: ...
  - Cubre: ...

## Fase 4 — Validación

- [ ] **T00X** Ejecutar el caso de referencia y registrar el puntaje
- [ ] **T00X** Ejecutar el caso de generalización y registrar el puntaje
- [ ] **T00X** Verificar que no haya datos inventados (Art. II)

## Fase 5 — Cierre

- [ ] **T00X** Actualizar documentación (`README` del componente, `CHANGELOG`)
- [ ] **T00X** Abrir Pull Request hacia `main` con la checklist completa
