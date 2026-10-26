# Mapa de funcionalidades de V.I.D.A.

*Vortexbird Intelligent Documentation Assistant*

**Versión:** 1.0
**Fecha:** 2026-10-25
**Responsable del proyecto:** Diego Moreno (Requirements Owner)

Este documento lista las funcionalidades del **módulo de documentación**, el primero de la plataforma, con su alcance, sus dependencias y su estado. No es una especificación ni un plan: no define *cómo* se construye nada. Cada funcionalidad se especifica a su turno con `/sdd-especificar`, en su propia rama `feature/NNN-nombre`, según el Artículo XI de la [constitución](constitucion.md).

El orden de la numeración es el orden previsto de construcción: avanzamos **una funcionalidad a la vez** y la siguiente no empieza hasta que la anterior se integra en `main`.

---

## Resumen

| N.º | Funcionalidad | Depende de | Estado |
|---|---|---|---|
| 001 | Acceso y roles | — | Pendiente |
| 002 | Tipos de documentación | 001 | Pendiente |
| 003 | Carga de información de una actividad | 002 | Pendiente |
| 004 | Análisis y preguntas | 003 | Pendiente |
| 005 | Generación y evaluación | 004, 007 | Pendiente |
| 006 | Revisión, historial y descarga | 005 | Pendiente |
| 007 | Parámetros editables | 001 | Pendiente |

---

## 001 — Acceso y roles

**Estado:** Pendiente
**Depende de:** —

**Qué cubre**

- Autenticación de usuarios: solo usuarios autenticados usan la plataforma.
- Dos roles: **RO** y **Administrador**, con permisos distintos.
- Base sobre la que las demás funcionalidades deciden quién puede hacer qué: el Administrador define tipos de documentación y parámetros; el RO carga información y genera documentos.

## 002 — Tipos de documentación

**Estado:** Pendiente
**Depende de:** 001 (solo el Administrador crea tipos)

**Qué cubre**

- El Administrador crea los tipos de documentación disponibles en la plataforma.
- Para cada tipo carga su **formato** en Word o Excel.
- Al cargarlo, el sistema **reconoce la estructura** del formato (secciones, hojas, columnas, orden y nombres) y la conserva tal como viene. El análisis del formato se hace una sola vez, al cargarlo.
- Esa estructura reconocida es la que manda en la generación: el sistema no agrega, quita, renombra ni reordena nada (Artículo I).

## 003 — Carga de información de una actividad

**Estado:** Pendiente
**Depende de:** 002 (el RO elige un tipo de documentación existente)

**Qué cubre**

- El RO elige el tipo de documentación y abre una actividad.
- Carga la información de esa actividad con **archivos adjuntos, texto escrito, o ambos**.
- Los insumos quedan asociados a la actividad y disponibles para el análisis posterior.

## 004 — Análisis y preguntas

**Estado:** Pendiente
**Depende de:** 003 (necesita la información cargada)

**Qué cubre**

- El sistema analiza lo cargado frente a la estructura del formato e **identifica qué información falta**.
- **Pregunta** al RO por lo que falta.
- El RO **responde** o decide **dejarlo pendiente**; ninguna de las dos respuestas bloquea el avance (Artículo III).
- Ningún dato se completa por cuenta del sistema, aunque parezca obvio (Artículo II).

## 005 — Generación y evaluación

**Estado:** Pendiente
**Depende de:** 004 (necesita el análisis y las respuestas del RO), 007 (toma de ahí rúbrica, pesos, mínimo, iteraciones y modelo)

**Qué cubre**

- Genera el documento en el formato definido por el tipo de documentación, con lo que el RO cargó o respondió y los pendientes marcados como `PENDIENTE`.
- Un **evaluador independiente** del agente que genera califica el documento con una **rúbrica medible** (Artículo VII).
- Si no alcanza el puntaje mínimo dentro de las iteraciones permitidas, el documento pasa a **revisión humana**.
- Cada campo del documento generado queda trazable a su origen: archivo cargado, texto ingresado, respuesta del RO o pendiente (Artículo IX).

## 006 — Revisión, historial y descarga

**Estado:** Pendiente
**Depende de:** 005 (necesita documentos generados)

**Qué cubre**

- El RO revisa el documento generado y su calificación.
- **Historial** de los documentos generados por actividad, con sus versiones.
- **Descarga** del documento en su formato original (Word o Excel).

## 007 — Parámetros editables

**Estado:** Pendiente
**Depende de:** 001 (solo el Administrador edita parámetros)

**Qué cubre**

- Parámetros que no pueden quedar fijos en el código: **criterios de la rúbrica, pesos, puntaje mínimo, iteraciones máximas** y **modelo por tarea** (Artículos V y VII).
- **Mientras esta funcionalidad no exista, esos parámetros viven en configuración**, no en el código. Esta funcionalidad les pone interfaz de administración; no cambia el principio.

---

## Módulos futuros

Fuera del alcance del módulo de documentación. Se listan para no diseñar nada que los impida, no para construirlos ahora: la plataforma debe permitir agregar módulos sin rehacer lo existente. **No se crea estructura, carpetas ni código para estos módulos** hasta que tengan su propia especificación.

- **Pruebas de carga con K6.**
- **Análisis de comportamiento de APIs.**

---

## Registro de cambios

| Versión | Fecha | Autor | Cambio |
|---|---|---|---|
| 1.0 | 2026-10-25 | Diego Moreno | Mapa inicial: 7 funcionalidades del módulo de documentación y módulos futuros |
