# Guía de contribución

## Ramas

| Rama | Uso | Se crea desde | Se integra en |
|---|---|---|---|
| `main` | Versión estable. Nadie hace commit directo. | — | — |
| `feature/NNN-nombre` | Una especificación (funcionalidad o mejora). | `main` | `main` vía PR |
| `fix/NNN-descripcion` | Corrección sobre una spec ya integrada. `NNN` es la spec que se corrige. | `main` | `main` vía PR |
| `constitucion/vX.Y.Z` | Enmienda a la constitución. | `main` | `main` vía PR |

- Las ramas `feature/` se crean **solo** con `/speckit-specify`, para que la numeración no se repita.
- Cada rama se trabaja en su propio worktree, creado con `bash scripts/nuevo-worktree.sh <NNN>`.
- Antes de abrir el PR, actualiza tu rama con `main` (`git pull --rebase origin main`).
- Una rama se elimina después de integrarse.

## Trabajo en paralelo

Varias funcionalidades pueden avanzar al mismo tiempo, una por persona y cada una en su rama. Dos reglas, un worktree por rama y tres cuidados.

**Las dos reglas**

1. **No se implementa una funcionalidad cuyas dependencias no estén integradas en `main`.** De cuál depende cada una lo dice [`.specify/memory/mapa-funcionalidades.md`](.specify/memory/mapa-funcionalidades.md). Hoy, por ejemplo, la 003 no se puede implementar hasta que la 002 esté en `main`.
2. **Escribir la spec y el plan nunca está bloqueado.** No necesitan el código de la funcionalidad anterior. Lo que espera es `/speckit-implement`, no `/speckit-specify`. Mientras alguien implementa, otra persona puede dejar listas las especificaciones que vienen.

**Un worktree por rama**

Un worktree es una copia de trabajo más del mismo repositorio, en otra carpeta y con otra rama
puesta. Sirve para tener dos funcionalidades abiertas a la vez sin cambiar de rama ni perder el
entorno de la otra:

```bash
bash scripts/nuevo-worktree.sh 002              # la rama feature/002-... ya debe existir
bash scripts/nuevo-worktree.sh 002 --con-base   # además levanta PostgreSQL y aplica migraciones
```

El script hace lo que `git worktree add` no hace por sí solo:

- Copia tu `.env`, que está en `.gitignore` (Art. X.2) y por eso no viaja al worktree nuevo.
- **Desplaza los puertos por número de spec**, para que dos worktrees corriendo a la vez no
  compitan. El checkout principal se queda con los de siempre:

  | | PostgreSQL | Backend | Front |
  |---|---|---|---|
  | Checkout principal | 55432 | 8000 | 3000 |
  | Worktree `NNN` | 55000 + NNN | 8000 + NNN | 3000 + NNN |
  | Ejemplo: `002` | 55002 | 8002 | 3002 |

- Crea el `.venv` del backend y los `node_modules` del front. Tampoco se comparten entre
  worktrees, así que cada uno necesita los suyos.

Los worktrees viven en `../vida-worktrees/NNN-nombre`, **fuera** del repositorio, para que no
aparezcan como archivos sin seguimiento.

Tres cosas que conviene saber:

- **Cada worktree tiene su propia base de datos, y nace vacía.** Compose nombra el proyecto y el
  volumen por carpeta, así que los usuarios que creaste en el checkout principal no están ahí:
  hay que correr `alembic upgrade head` y `scripts.crear_admin` en cada worktree.
- **`.specify/feature.json` es local a cada worktree** y no se versiona. Es el puntero a la spec
  en la que Spec Kit está trabajando, y por eso cada worktree lleva el suyo.
- **Cuando la rama se integre a `main`, borra el worktree:** `git worktree remove ../vida-worktrees/NNN-nombre`.
  Si no, `git worktree list` se llena de carpetas de ramas que ya no existen.

**Cuidado 1 — La numeración de las specs**

Crea la rama **solo** con `/speckit-specify`. No crees ramas `feature/NNN-...` a mano.

Spec Kit numera mirando únicamente las carpetas de `specs/` del checkout donde se ejecuta, y eso
no alcanza aquí: el mapa reserva del 001 al 007, las tomamos salteadas, y un worktree no ve las
carpetas de spec que viven en la rama de otro. Por eso el número lo calcula un script del
proyecto, que **consulta el remoto** antes de responder:

```bash
bash scripts/numero-de-spec.sh                 # el siguiente libre
SDD_NUMERO=007 bash scripts/numero-de-spec.sh  # valida un número que el mapa reserva
```

Ese valor se le pasa a Spec Kit como `--number`. Sin él, Spec Kit toma el número más alto que
exista en el disco y le suma uno. Dos consecuencias concretas:

- Pedir la 007 cuando la más alta es la 004 daría una `005`, que en el mapa es otra funcionalidad.
- Una vez que existe la `007`, el modo automático pasa a dar `008` y se salta la 003, la 004, la 005 y la 006.

Así que **mientras queden números del mapa sin usar, pasa `SDD_NUMERO`**. El modo automático queda
para las specs que vengan después del mapa, de la 008 en adelante. El script rechaza un número ya
tomado y uno que no sean tres dígitos.

Si Spec Kit avisa `--number NNN conflicts with an existing spec directory; using MMM instead`,
**detente**: no es un aviso menor, significa que el número del mapa ya estaba tomado.

**Cuidado 2 — Las migraciones de la base de datos**

Si dos ramas generan cada una su migración desde el mismo punto, al juntarlas quedan **dos cabezas** y `alembic upgrade head` falla.

> **Convención: quien mezcla segundo regenera su migración.**

En concreto, cuando tu rama ya tiene una migración y entra otra a `main` antes que la tuya:

```bash
git pull --rebase origin main
cd backend
.venv/Scripts/python -m alembic history          # confirma que hay dos cabezas
# borra tu archivo de migración y vuelve a generarlo sobre la cabeza nueva
rm alembic/versions/<tu-migracion>.py
.venv/Scripts/python -m alembic revision --autogenerate -m "<tu descripción>"
.venv/Scripts/python -m alembic upgrade head     # debe aplicar sin error
```

Regenerar es más seguro que editar el `down_revision` a mano, porque además recalcula el contenido contra el esquema que dejó la otra rama. Si tu migración llevaba datos o pasos escritos a mano, cópialos al archivo nuevo antes de borrar el viejo.

**Cuidado 3 — Los archivos que todas las ramas tocan**

Estos van a dar conflicto, y son conflictos pequeños y previsibles. Al resolverlos, **conserva las dos partes**: casi nunca una reemplaza a la otra.

| Archivo | Qué agrega cada funcionalidad |
|---|---|
| `backend/app/main.py` | El registro de su enrutador |
| `backend/app/modelos/__init__.py` | La importación de sus modelos |
| `frontend/app/componentes/menu-por-rol.tsx` | Su opción en el menú |
| `.env.ejemplo` | Sus variables de configuración |
| `README.md` y `.specify/memory/mapa-funcionalidades.md` | Su estado |

## Commits

Formato: `<tipo>(<spec>): <descripción en minúscula>`

| Tipo | Cuándo |
|---|---|
| `spec(NNN)` | Crear o ajustar la especificación |
| `plan(NNN)` | Crear o ajustar el plan |
| `tareas(NNN)` | Crear o ajustar las tareas |
| `TNNN` | Implementación de una tarea (ej. `T004: agrega lector de hoja Request`) |
| `constitucion` | Enmienda (`constitucion: v1.1.0 - agrega artículo de auditoría`) |
| `docs` / `chore` | Documentación general o mantenimiento |

## Pull Request hacia `main`

Título: `[NNN] Nombre de la especificación`

Checklist obligatoria en la descripción del PR:

```markdown
- [ ] La spec no tiene marcas [NECESITA ACLARACIÓN] abiertas que afecten el alcance
- [ ] plan.md incluye la verificación contra la constitución
- [ ] Todas las tareas de tasks.md están en [x]
- [ ] `/speckit-analyze` no reporta inconsistencias entre spec, plan y tareas
- [ ] Se validó con el caso de referencia y con al menos un caso distinto
- [ ] Sin secretos, keys ni datos reales de clientes en el diff
- [ ] Documentación actualizada
```

**Aprobación:** mínimo una revisión de otro integrante del área RO. Las enmiendas a la constitución solo entran por Pull Request y requieren aprobación del responsable del proyecto.

## Qué nunca se sube

- Archivos `.env`, keys, tokens, credenciales o cookies.
- Documentos con datos reales de clientes, cuentas o personas.
- Archivos cargados por los RO o documentos generados con datos reales.
