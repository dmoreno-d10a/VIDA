# Tareas: [NOMBRE DE LA FUNCIONALIDAD]

**Spec:** [`spec.md`](./spec.md) · **Plan:** [`plan.md`](./plan.md)
**Rama:** `feature/[NNN-nombre-corto]`
**Insumos:** `plan.md` (obligatorio), `spec.md` (obligatorio, de ahí salen las historias),
`research.md`, `data-model.md`, `contracts/` (si el plan los generó)

> **Reglas**
>
> - Cada tarea es pequeña, verificable y tiene un criterio de terminado.
> - `[P]` indica que la tarea puede hacerse en paralelo con otras `[P]` de la misma fase.
> - `[HU-N]` indica a qué historia de usuario pertenece la tarea.
> - Se marca `[x]` solo cuando el criterio de terminado se cumple.
> - Un commit por tarea, con el ID en el mensaje: `T003: descripción`.
> - **Las pruebas no son opcionales en este proyecto.** El Art. VIII exige validar cada
>   capacidad con al menos un caso distinto al de referencia.
>
> **Organización:** las tareas se agrupan por historia de usuario, en orden de prioridad, para
> que cada historia pueda implementarse y probarse sola. Las fases 1 y 2 son compartidas y
> bloquean a todas las historias.

**Formato:** `[ID] [P] [HU-N] descripción`

---

## Fase 1 — Preparación

**Propósito:** estructura y dependencias que necesita todo lo demás.

- [ ] **T001** [descripción]
  - Terminado cuando: [criterio verificable]
  - Cubre: [RF-XX / HU-X]

## Fase 2 — Base compartida (bloquea a todas las historias)

**Propósito:** lo que debe existir antes de poder empezar cualquier historia: esquema de base
de datos y migración, modelos base, autorización, manejo de errores, configuración.

**Ninguna historia puede empezar antes de cerrar esta fase.**

- [ ] **T00X** [descripción]
  - Terminado cuando: ...

**Punto de control:** con la base lista, las historias pueden avanzar en paralelo.

## Fase 3 — Casos de prueba primero

**Propósito:** fijar el resultado esperado antes de construir, para que el Art. II (cero
información inventada) sea verificable y no una opinión.

- [ ] **T00X** [P] Definir la respuesta esperada del caso de referencia
  - Terminado cuando: existe la respuesta esperada del caso, en la ruta definida en el plan
- [ ] **T00X** [P] Definir la respuesta esperada del caso de generalización
  - Terminado cuando: existe la respuesta esperada de un caso distinto al de referencia (Art. VIII)

## Fase 4 — HU-1: [título] (Prioridad: P1) 🎯 MVP

**Objetivo:** [qué entrega esta historia]
**Prueba independiente:** [cómo se verifica sola]

- [ ] **T00X** [P] [HU-1] [descripción]
  - Terminado cuando: ...
  - Cubre: [RF-XX]

**Punto de control:** HU-1 funciona y se puede demostrar por sí sola.

## Fase 5 — HU-2: [título] (Prioridad: P2)

**Objetivo:** [qué entrega esta historia]
**Prueba independiente:** [cómo se verifica sola]

- [ ] **T00X** [P] [HU-2] [descripción]
  - Terminado cuando: ...

**Punto de control:** HU-2 funciona sin romper HU-1.

## Fase 6 — Validación

- [ ] **T00X** Ejecutar el caso de referencia y registrar el puntaje
- [ ] **T00X** Ejecutar el caso de generalización y registrar el puntaje (Art. VIII)
- [ ] **T00X** Verificar que no haya datos inventados (Art. II)
- [ ] **T00X** Verificar que cada campo generado sea rastreable a su origen (Art. IX)

## Fase 7 — Cierre

- [ ] **T00X** Actualizar documentación (`README` del componente, `CHANGELOG`)
- [ ] **T00X** Actualizar el estado de la funcionalidad en `.specify/memory/mapa-funcionalidades.md`
- [ ] **T00X** Abrir Pull Request hacia `main` con la checklist completa
