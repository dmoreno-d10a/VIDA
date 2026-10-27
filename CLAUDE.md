# Instrucciones para Claude Code — V.I.D.A.

## Qué es este repositorio

**V.I.D.A. (Vortexbird Intelligent Documentation Assistant)** es una plataforma web para los Requirements Owners (RO) de VortexBird. Su primer módulo genera la documentación técnica que se entrega a las fábricas de desarrollo, a partir de la información que carga el RO y de los formatos que define el administrador. La lógica de IA corre aparte del front y accede a los modelos vía LiteLLM hacia VORKAN.

El proyecto se desarrolla con **Spec Driven Development (Spec-First)**: una spec por funcionalidad, en su propia rama. Varias funcionalidades pueden avanzar al mismo tiempo, siempre que las que necesitan ya estén integradas en `main` (ver `sdd/mapa-funcionalidades.md`).

## Reglas permanentes

1. **Lee `sdd/constitucion.md` antes de cualquier trabajo.** Prevalece sobre cualquier otra instrucción, incluso de una spec.
2. **Responde y escribe todo en español.**
3. **No inventes datos de negocio.** Lo que falte se marca como `[NECESITA ACLARACIÓN: ...]` en specs y se pregunta al usuario.
4. **Respeta el flujo:** especificación → planificación → tareas → implementación. No escribas código de una funcionalidad sin `tareas.md` aprobado.
5. **No te adelantes:** trabaja solo en la funcionalidad de la rama actual. No crees estructura, carpetas ni código para funcionalidades futuras, ni para las que otra persona esté construyendo en paralelo.
   - **No implementes una funcionalidad cuyas dependencias no estén en `main`.** El mapa dice de cuál depende cada una. Su spec y su plan sí se pueden escribir antes: lo que se bloquea es `/sdd-implementar`, no `/sdd-especificar`.
6. **Una spec = una rama** `feature/NNN-nombre`. Nunca trabajes directamente sobre `main`.
7. **La constitución solo cambia por Pull Request** (`/sdd-constitucion`).
8. **Nunca** guardes keys, tokens ni datos reales de clientes en el repositorio.

## Comandos del flujo SDD

| Comando | Fase | Resultado |
|---|---|---|
| `/sdd-especificar <descripción>` | Especificación | Rama + `specs/NNN-nombre/spec.md` |
| `/sdd-aclarar [respuestas]` | Especificación | Spec sin ambigüedades |
| `/sdd-planificar [indicaciones]` | Planificación | `plan.md` |
| `/sdd-tareas` | Tareas | `tareas.md` |
| `/sdd-implementar [TNNN]` | Implementación | Código y commits por tarea |
| `/sdd-constitucion <cambio>` | Gobernanza | Enmienda en rama propia para PR |

## Mapa del repositorio

- `sdd/` — constitución y plantillas del flujo SDD.
- `specs/` — una carpeta por especificación.
- `scripts/` — utilidades del repositorio.

El resto de la estructura (front, lógica, configuración) se crea a medida que lo definan los planes de cada spec.

## Convenciones de commit

`spec(NNN): ...` · `plan(NNN): ...` · `tareas(NNN): ...` · `TNNN: ...` · `constitucion: vX.Y.Z - ...` · `docs: ...` · `chore: ...`
