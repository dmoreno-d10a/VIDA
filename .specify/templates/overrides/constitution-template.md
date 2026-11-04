# Constitución de V.I.D.A.

*Vortexbird Intelligent Documentation Assistant*

**Versión:** [vX.Y.Z]
**Fecha de ratificación:** [AAAA-MM-DD]
**Responsable del proyecto:** [nombre] (Requirements Owner)

> **ATENCIÓN — ESTE ARCHIVO NO SE EDITA EN LA RAMA DE UNA FUNCIONALIDAD.**
>
> La constitución solo cambia por **Pull Request dedicado**, en una rama `constitucion/vX.Y.Z`.
> Si `/speckit-constitution` se invoca desde una rama `feature/NNN-...`, hay que detenerse,
> crear la rama de constitución y proponer la enmienda allí. Ver *Gobernanza*.

Esta constitución reúne los principios no negociables del proyecto. Toda especificación, plan,
tarea e implementación debe cumplirlos. Si algo entra en conflicto con un artículo, prevalece la
constitución, y el conflicto se resuelve enmendándola, nunca ignorándola.

---

## Propósito

[Qué es V.I.D.A. y qué debe seguir siendo cierto a medida que crece.]

## Artículo I — [NOMBRE DEL PRINCIPIO]

[Enunciado del principio. Debe ser verificable: un plan tiene que poder decir "sí cumple" o
"no cumple" y explicar cómo.]

## Artículo II — [NOMBRE DEL PRINCIPIO]

[...]

<!-- Agregar un artículo por principio no negociable. Numeración romana, continua y estable:
     un artículo nunca se renumera, porque las specs y los planes lo citan por su número. -->

---

## Gobernanza

- Esta constitución solo se modifica mediante un **Pull Request dedicado** (rama
  `constitucion/vX.Y.Z`). No se admiten cambios directos sobre `main` ni desde una rama de
  funcionalidad.
- El PR requiere la aprobación del responsable del proyecto.
- Versionado:
  - **MAJOR:** se elimina un artículo o se cambia su sentido.
  - **MINOR:** se agrega un artículo o se amplía uno existente.
  - **PATCH:** redacción, ortografía o aclaraciones sin cambio de sentido.
- Cada plan (`plan.md`) incluye una verificación explícita contra esta constitución.

## Registro de enmiendas

| Versión | Fecha | Autor | Cambio |
|---|---|---|---|
| [vX.Y.Z] | [AAAA-MM-DD] | [autor] | [qué cambió y por qué] |
