# Especificación: Parámetros editables

**ID:** 007
**Rama:** `feature/007-parametros-editables`
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

> Van **ordenadas por prioridad** (P1 es la más crítica). Cada historia debe poder probarse
> por sí sola: si se implementara solo esa, el resultado ya debería entregar valor.

### HU-1: [título corto] (Prioridad: P1)

**Como** [rol], **quiero** [acción], **para** [beneficio].

**Por qué esta prioridad:** [qué valor entrega y por qué va primero]

**Prueba independiente:** [cómo se verifica esta historia sola, sin las demás]

**Criterios de aceptación:**

- **Dado** [contexto], **cuando** [acción], **entonces** [resultado esperado].
- **Dado** ..., **cuando** ..., **entonces** ...

### HU-2: [título corto] (Prioridad: P2)

**Como** [rol], **quiero** [acción], **para** [beneficio].

**Por qué esta prioridad:** [...]

**Prueba independiente:** [...]

**Criterios de aceptación:**

- **Dado** ..., **cuando** ..., **entonces** ...

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

## 6. Entidades principales *(si la funcionalidad maneja datos)*

- **[Entidad 1]:** [qué representa y sus atributos clave, sin hablar de implementación]
- **[Entidad 2]:** [qué representa y su relación con las demás]

## 7. Casos borde y errores

- [Qué pasa si falta un insumo]
- [Qué pasa si los insumos se contradicen]
- [Qué pasa si el Evaluador no aprueba tras las iteraciones permitidas]

## 8. Fuera de alcance

- [Lo que explícitamente NO cubre esta spec]

## 9. Supuestos

> Lo que se asumió como razonable porque la descripción no lo precisaba. Un supuesto no
> reemplaza una aclaración: si afecta el alcance, va en la sección 11.

- [Supuesto sobre los usuarios, el entorno o los límites del alcance]

## 10. Criterios de éxito medibles

- **CE-01:** [ej. Puntaje del Evaluador ≥ 95/100 en el caso de referencia y en el caso ficticio]
- **CE-02:** [ej. 0 campos inventados]

> Medibles y sin tecnología: describen el resultado observable, no cómo se logra.

## 11. Pendientes y preguntas abiertas

> Todo lo que no se sabe se marca aquí como `[NECESITA ACLARACIÓN: ...]`, **máximo 3 marcas**.
> Si hay más, se priorizan las que afectan el alcance. La spec no pasa a planificación con
> aclaraciones abiertas que afecten el alcance.

- [NECESITA ACLARACIÓN: ...]

## 12. Verificación contra la constitución

- [ ] Respeta la estructura de los formatos definidos (Art. I)
- [ ] No exige completar datos que no estén en los insumos ni en las respuestas del RO (Art. II y III)
- [ ] Contempla al menos un caso distinto al de referencia (Art. VIII)
- [ ] No define tecnologías ni implementación (Art. XI)
- [ ] Está escrita en español (Art. XII)
