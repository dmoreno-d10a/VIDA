#!/usr/bin/env bash
# Prepara un worktree de git para trabajar una funcionalidad en paralelo, con su
# propio entorno: .env con puertos que no chocan, venv del backend y node_modules
# del front.
#
# Uso:
#   bash scripts/nuevo-worktree.sh 002                        # por número
#   bash scripts/nuevo-worktree.sh 002-tipos-de-documentacion # por nombre completo
#   bash scripts/nuevo-worktree.sh feature/007-parametros-editables
#   bash scripts/nuevo-worktree.sh 002 --con-base             # además levanta la base y migra
#
# La rama tiene que existir ya. Para crearla, usa /speckit-specify: es quien
# numera la spec y crea la carpeta.
#
# Por qué hace falta un script y no basta `git worktree add`:
#
#   - `.env` está en .gitignore (Art. X.2), así que no viaja al worktree nuevo.
#   - Dos worktrees corriendo a la vez competirían por los puertos de PostgreSQL,
#     del backend y del front. Este script los desplaza por número de spec.
#   - `.venv` y `node_modules` tampoco se comparten entre worktrees: cada uno
#     necesita los suyos.
#
# Puertos por worktree (el checkout principal se queda con 55432 / 8000 / 3000):
#
#   PostgreSQL   55000 + NNN     (002 -> 55002)
#   Backend       8000 + NNN     (002 -> 8002)
#   Front         3000 + NNN     (002 -> 3002)
set -euo pipefail

CON_BASE=0
ARG=""
for a in "$@"; do
  case "$a" in
    --con-base) CON_BASE=1 ;;
    -h|--help)
      sed -n '2,30p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    -*) echo "Opción desconocida: $a" >&2; exit 1 ;;
    *)  ARG="$a" ;;
  esac
done

if [ -z "$ARG" ]; then
  echo "Uso: bash scripts/nuevo-worktree.sh <NNN | NNN-nombre | feature/NNN-nombre> [--con-base]" >&2
  exit 1
fi

RAIZ=$(git rev-parse --show-toplevel)
cd "$RAIZ"

# --- Resolver la rama -------------------------------------------------------

git fetch --prune origin >/dev/null 2>&1 || \
  echo "Aviso: no se pudo consultar el remoto; se busca la rama solo entre las locales." >&2

case "$ARG" in
  feature/*) RAMA="$ARG" ;;
  [0-9][0-9][0-9]-*) RAMA="feature/$ARG" ;;
  [0-9][0-9][0-9])
    # Solo el número: se busca la rama que lo lleva, local o del remoto.
    RAMA=$(git branch -a --format='%(refname:short)' \
           | sed 's|^origin/||' \
           | grep -E "^feature/${ARG}-" \
           | sort -u | head -1 || true)
    if [ -z "$RAMA" ]; then
      echo "No encontré ninguna rama feature/${ARG}-… ni local ni en el remoto." >&2
      echo "Si la funcionalidad todavía no tiene spec, créala con /speckit-specify." >&2
      exit 1
    fi
    ;;
  *)
    echo "No entiendo '$ARG'. Espero NNN, NNN-nombre o feature/NNN-nombre." >&2
    exit 1 ;;
esac

NOMBRE=${RAMA#feature/}
NUM=$(echo "$NOMBRE" | cut -c1-3)

if ! echo "$NUM" | grep -qE '^[0-9]{3}$'; then
  echo "La rama '$RAMA' no sigue el formato feature/NNN-nombre (Art. XI)." >&2
  exit 1
fi

# La rama debe existir. Si solo está en el remoto, se crea el seguimiento local.
if git show-ref --verify --quiet "refs/heads/$RAMA"; then
  ORIGEN=()
elif git show-ref --verify --quiet "refs/remotes/origin/$RAMA"; then
  ORIGEN=(-b "$RAMA" --track "origin/$RAMA")
else
  echo "La rama '$RAMA' no existe. Créala con /speckit-specify." >&2
  exit 1
fi

# --- Crear el worktree ------------------------------------------------------

DESTINO="$(dirname "$RAIZ")/vida-worktrees/$NOMBRE"

if [ -e "$DESTINO" ]; then
  echo "Ya existe algo en $DESTINO." >&2
  echo "Si es un worktree que ya no usas: git worktree remove \"$DESTINO\"" >&2
  exit 1
fi

mkdir -p "$(dirname "$DESTINO")"

if [ ${#ORIGEN[@]} -gt 0 ]; then
  git worktree add "${ORIGEN[@]}" "$DESTINO"
else
  git worktree add "$DESTINO" "$RAMA"
fi

# --- .env con puertos propios ----------------------------------------------

PUERTO_BD=$((55000 + 10#$NUM))
PUERTO_API=$((8000 + 10#$NUM))
PUERTO_FRONT=$((3000 + 10#$NUM))

if [ -f "$RAIZ/.env" ]; then
  # Se parte del .env del checkout principal para no volver a pedir la
  # contraseña local, y solo se reescriben los puertos.
  sed -e "s|^VIDA_BD_PUERTO=.*|VIDA_BD_PUERTO=${PUERTO_BD}|" \
      -e "s|\(^VIDA_BD_URL=.*@[^:]*\):[0-9]\{1,5\}/|\1:${PUERTO_BD}/|" \
      -e "s|^VIDA_API_URL=.*|VIDA_API_URL=http://localhost:${PUERTO_API}|" \
      "$RAIZ/.env" > "$DESTINO/.env"
  echo "" >> "$DESTINO/.env"
  echo "# --- Worktree $NOMBRE: puertos desplazados por scripts/nuevo-worktree.sh ---" >> "$DESTINO/.env"
  echo "# PostgreSQL $PUERTO_BD · backend $PUERTO_API · front $PUERTO_FRONT" >> "$DESTINO/.env"
  echo ".env copiado del checkout principal, con los puertos cambiados."
else
  cp "$RAIZ/.env.ejemplo" "$DESTINO/.env"
  sed -i -e "s|^VIDA_BD_PUERTO=.*|VIDA_BD_PUERTO=${PUERTO_BD}|" \
         -e "s|\(^VIDA_BD_URL=.*@[^:]*\):[0-9]\{1,5\}/|\1:${PUERTO_BD}/|" \
         -e "s|^VIDA_API_URL=.*|VIDA_API_URL=http://localhost:${PUERTO_API}|" \
         "$DESTINO/.env"
  echo "Aviso: no hay .env en el checkout principal, así que se copió .env.ejemplo."
  echo "       Define VIDA_BD_CONTRASENA en $DESTINO/.env antes de levantar la base."
fi

# --- Dependencias -----------------------------------------------------------

echo "Creando el entorno de Python del backend…"
python -m venv "$DESTINO/backend/.venv"
if [ -x "$DESTINO/backend/.venv/Scripts/python" ]; then
  PY="$DESTINO/backend/.venv/Scripts/python"   # Windows
else
  PY="$DESTINO/backend/.venv/bin/python"       # Linux o macOS
fi
(cd "$DESTINO/backend" && "$PY" -m pip install -q -e ".[dev]")

echo "Instalando las dependencias del front…"
(cd "$DESTINO/frontend" && npm ci --silent)

# --- Base de datos (opcional) ----------------------------------------------

if [ "$CON_BASE" = "1" ]; then
  echo "Levantando PostgreSQL para este worktree…"
  # Compose nombra el proyecto y el volumen por la carpeta, así que este
  # worktree obtiene su propia base, vacía y aparte de las demás.
  (cd "$DESTINO" && docker compose up -d)
  echo "Aplicando las migraciones…"
  (cd "$DESTINO/backend" && "$PY" -m alembic upgrade head)
  echo "Falta el primer Administrador de esta base:"
  echo "    cd \"$DESTINO/backend\" && .venv/Scripts/python -m scripts.crear_admin"
fi

# --- Resumen ----------------------------------------------------------------

cat <<RESUMEN

Worktree listo.

  Rama:       $RAMA
  Carpeta:    $DESTINO
  PostgreSQL: $PUERTO_BD
  Backend:    $PUERTO_API
  Front:      $PUERTO_FRONT

Para trabajar ahí:

  cd "$DESTINO"
RESUMEN

if [ "$CON_BASE" != "1" ]; then
  cat <<RESUMEN
  docker compose up -d
  cd backend && .venv/Scripts/python -m alembic upgrade head
  cd backend && .venv/Scripts/python -m scripts.crear_admin
RESUMEN
fi

cat <<RESUMEN
  cd backend  && .venv/Scripts/python -m uvicorn app.main:app --port $PUERTO_API
  cd frontend && npm run dev -- --port $PUERTO_FRONT
  claude

Este worktree tiene su propia base, vacía: Compose la nombra por carpeta. Los
usuarios del checkout principal no están ahí.

Cuando la rama se integre a main:

  git worktree remove "$DESTINO"
RESUMEN
