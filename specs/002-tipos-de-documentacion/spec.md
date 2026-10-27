# Especificación: [NOMBRE DE LA FUNCIONALIDAD]

**ID:** 002
**Rama:** `feature/002-tipos-de-documentacion`
**Autor:** [nombre]
**Fecha:** 2026-10-26
**Estado:** Borrador | En revisión | Aprobada

> Una spec describe **qué** se necesita y **por qué**. No incluye tecnologías, librerías, estructura de código ni prompts. Eso va en `plan.md`.

---

## 1. Contexto y problema

[Qué situación del área RO motiva esta funcionalidad. Qué pasa hoy y por qué es un problema.]

## 2. Usuarios

[Quién usa esta funcionalidad: RO, Administrador, fábrica que recibe el documento, revisor humano, etc.]

## 3. Historias de usuario

### HU-1: [título corto]
**Como** [rol], **quiero** [acción], **para** [beneficio].

**Criterios de aceptación:**
- **Dado** [contexto], **cuando** [acción], **entonces** [resultado esperado].
- **Dado** ..., **cuando** ..., **entonces** ...

### HU-2: [título corto]
...

## 4. Requerimientos funcionales

| ID | Requerimiento |
|---|---|
| RF-01 | El sistema debe ... |
| RF-02 | El sistema debe ... |

## 5. Entradas y salidas

| Tipo | Elemento | Formato | Origen / destino |
|---|---|---|---|
| Entrada | [ej. contexto del servicio] | [.md / .json / .xlsx] | [quién lo entrega] |
| Salida | [ej. documento generado] | [.docx / .xlsx] | [fábrica de desarrollo] |

## 6. Casos borde y errores

- [Qué pasa si falta un insumo]
- [Qué pasa si los insumos se contradicen]
- [Qué pasa si el Evaluador no aprueba tras 3 iteraciones]

## 7. Fuera de alcance

- [Lo que explícitamente NO cubre esta spec]

## 8. Criterios de éxito medibles

- [ej. Puntaje del Evaluador ≥ 95/100 en el caso de referencia y en el caso ficticio]
- [ej. 0 campos inventados]

## 9. Pendientes y preguntas abiertas

> Todo lo que no se sabe se marca aquí como `[NECESITA ACLARACIÓN: ...]`. La spec no pasa a planificación con aclaraciones abiertas que afecten el alcance.

- [NECESITA ACLARACIÓN: ...]

## 10. Verificación contra la constitución

- [ ] Respeta la estructura de los formatos definidos (Art. I)
- [ ] No exige completar datos que no estén en los insumos ni en las respuestas del RO (Art. II y III)
- [ ] Contempla al menos un caso distinto al de referencia (Art. VIII)
- [ ] No define tecnologías ni implementación (Art. XI)
