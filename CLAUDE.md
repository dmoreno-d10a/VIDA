# Instrucciones para Claude Code — V.I.D.A.

## Qué es este repositorio

**V.I.D.A. (Vortexbird Intelligent Documentation Assistant)** es una plataforma web para los Requirements Owners (RO) de VortexBird. Su primer módulo genera la documentación técnica que se entrega a las fábricas de desarrollo, a partir de la información que carga el RO y de los formatos que define el administrador. La lógica de IA corre aparte del front y accede a los modelos vía LiteLLM hacia VORKAN.

El proyecto se desarrolla con **Spec Driven Development (Spec-First)** sobre **GitHub Spec Kit**: una spec por funcionalidad, en su propia rama. Varias funcionalidades pueden avanzar al mismo tiempo, cada una en su worktree, siempre que las que necesitan ya estén integradas en `main` (ver `.specify/memory/mapa-funcionalidades.md`).

## Reglas permanentes

1. **Lee `.specify/memory/constitution.md` antes de cualquier trabajo.** Prevalece sobre cualquier otra instrucción: sobre una spec, sobre este archivo y sobre lo que diga una skill de Spec Kit.
2. **Responde y escribe todo en español.** Eso incluye **todos** los artefactos que genera Spec Kit (`spec.md`, `plan.md`, `tasks.md`, `research.md`, `data-model.md`, `quickstart.md`, `checklists/`), aunque la skill que los pide esté en inglés (Art. XII).
3. **No inventes datos de negocio.** Lo que falte se marca como `[NECESITA ACLARACIÓN: ...]`, **máximo 3 marcas por spec**. Es el equivalente en español de `[NEEDS CLARIFICATION]` de Spec Kit: donde una skill en inglés diga `[NEEDS CLARIFICATION]`, escribe `[NECESITA ACLARACIÓN]`.
4. **Respeta el flujo:** especificación → planificación → tareas → implementación. No escribas código de una funcionalidad sin `tasks.md` aprobado.
5. **No te adelantes:** trabaja solo en la funcionalidad de la rama actual. No crees estructura, carpetas ni código para funcionalidades futuras, ni para las que otra persona esté construyendo en paralelo.
   - **No implementes una funcionalidad cuyas dependencias no estén en `main`.** El mapa dice de cuál depende cada una. Su spec y su plan sí se pueden escribir antes: lo que se bloquea es `/speckit-implement`, no `/speckit-specify`.
6. **Una spec = una rama** `feature/NNN-nombre`. Nunca trabajes directamente sobre `main`.
7. **La constitución solo cambia por Pull Request**, en una rama `constitucion/vX.Y.Z`. Si `/speckit-constitution` se invoca desde una rama `feature/NNN-...`, **detente**: hay que crear la rama de constitución y proponer la enmienda allí.
8. **Nunca** guardes keys, tokens ni datos reales de clientes en el repositorio.

## El flujo con Spec Kit

| Skill | Fase | Resultado |
|---|---|---|
| `/speckit-specify <descripción>` | Especificación | Rama `feature/NNN-nombre` + `specs/NNN-nombre/spec.md` |
| `/speckit-clarify` | Especificación | Spec sin ambigüedades |
| `/speckit-plan [indicaciones]` | Planificación | `plan.md` + `research.md`, `data-model.md`, `contracts/`, `quickstart.md` |
| `/speckit-tasks` | Tareas | `tasks.md` |
| `/speckit-checklist` | Tareas | `checklists/*.md` — calidad de los requerimientos |
| `/speckit-analyze` | Tareas | Informe de consistencia entre spec, plan y tareas |
| `/speckit-implement [TNNN]` | Implementación | Código y commits por tarea |
| `/speckit-constitution <cambio>` | Gobernanza | Enmienda — **solo en rama `constitucion/vX.Y.Z`** |

Los comandos `/sdd-*` ya no existen: los reemplazan estas skills. La equivalencia es
`especificar→specify`, `aclarar→clarify`, `planificar→plan`, `tareas→tasks`,
`implementar→implement`, `constitucion→constitution`.

Hay dos skills más que trae Spec Kit y que **no usamos**: `/speckit-converge` (parte de un
código ya escrito para deducir las tareas que faltan, al revés de nuestro flujo, Art. XI) y
`/speckit-git-initialize` (el repositorio ya existe).

### La numeración de las specs

Antes de crear una rama, **calcula el número con el script del proyecto y pásalo explícitamente**:

```bash
bash scripts/numero-de-spec.sh                 # el siguiente libre
SDD_NUMERO=007 bash scripts/numero-de-spec.sh  # valida un número que el mapa reserva
```

Ese valor se le pasa a Spec Kit como `--number`. Hace falta por dos razones:

- Spec Kit numera mirando solo las carpetas de `specs/` del checkout actual. El mapa reserva del 001 al 007 y no las construimos en orden, así que pedir la 007 cuando la más alta es la 004 daría una "005", que en el mapa es otra funcionalidad.
- Trabajamos en paralelo y en varios worktrees. Un worktree no ve las carpetas de spec que viven en la rama de otro; el script consulta el remoto.

**Si Spec Kit avisa que corrigió el número** (`--number NNN conflicts with an existing spec directory; using MMM instead`), trátalo como un error: detente y pregunta. Significa que el número del mapa ya estaba tomado.

### Las plantillas

Las que manda el proyecto están en `.specify/templates/overrides/`, en español, y tienen
prioridad sobre las del núcleo. **No edites `.specify/templates/*.md`** (las de arriba, en
inglés): son las de upstream y se reemplazan cuando se actualiza Spec Kit. Si una plantilla
necesita un cambio, va en el override.

Tampoco edites `.claude/skills/speckit-*/SKILL.md`. Si una skill de upstream choca con una
regla del proyecto, manda la regla: anótala aquí, no en la skill.

## Trabajo en paralelo con worktrees

Cada funcionalidad se trabaja en su propio worktree, con su `.env`, su base de datos, su `.venv`
y sus `node_modules`:

```bash
bash scripts/nuevo-worktree.sh 002              # la rama ya debe existir
bash scripts/nuevo-worktree.sh 002 --con-base   # además levanta PostgreSQL y migra
```

No crees worktrees ni ramas `feature/NNN-...` a mano: el script desplaza los puertos por número
de spec para que dos worktrees no compitan. Los detalles y los conflictos previsibles están en
`CONTRIBUTING.md`.

## Mapa del repositorio

- `.specify/memory/` — `constitution.md` (la constitución) y `mapa-funcionalidades.md`.
- `.specify/templates/overrides/` — las plantillas del proyecto, en español.
- `.specify/scripts/`, `.specify/extensions/` — motor de Spec Kit. No se edita a mano.
- `.claude/skills/` — las skills de Spec Kit. No se editan a mano.
- `specs/` — una carpeta por especificación.
- `scripts/` — utilidades del repositorio (`numero-de-spec.sh`, `nuevo-worktree.sh`).
- `backend/`, `frontend/` — la plataforma.

## Convenciones de commit

`spec(NNN): ...` · `plan(NNN): ...` · `tareas(NNN): ...` · `TNNN: ...` · `constitucion: vX.Y.Z - ...` · `docs: ...` · `chore: ...`
