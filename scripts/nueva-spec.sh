#!/usr/bin/env bash
# Crea una nueva especificación SDD: rama feature/NNN-nombre + carpeta specs/NNN-nombre/
# Uso: bash scripts/nueva-spec.sh <nombre-corto-en-kebab-case>
#
# El número lo calcula el script: el siguiente al más alto que ya existe.
# Para fijarlo (cuando el mapa reserva uno y no construimos en orden):
#   SDD_NUMERO=007 bash scripts/nueva-spec.sh parametros-editables
set -euo pipefail

if [ $# -lt 1 ] || [ -z "$1" ]; then
  echo "Uso: bash scripts/nueva-spec.sh <nombre-corto>" >&2
  exit 1
fi

# Normaliza el nombre: minúsculas, sin tildes, solo [a-z0-9-]
NOMBRE=$(echo "$1" | sed -e 's/á/a/g; s/Á/a/g; s/é/e/g; s/É/e/g; s/í/i/g; s/Í/i/g; s/ó/o/g; s/Ó/o/g; s/ú/u/g; s/Ú/u/g; s/ü/u/g; s/Ü/u/g; s/ñ/n/g; s/Ñ/n/g')
NOMBRE=$(echo "$NOMBRE" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g')

RAIZ=$(git rev-parse --show-toplevel)
cd "$RAIZ"

# Verifica que no haya cambios sin guardar
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Hay cambios sin commit. Guárdalos o descártalos antes de crear una spec." >&2
  exit 1
fi

# Trae las ramas del remoto ANTES de calcular el número.
#
# Sin esto, dos personas que trabajan en paralelo y no han hecho fetch calculan
# el mismo número y crean dos specs "002" distintas. Si el remoto no responde,
# el script se detiene en vez de inventar un número con información vieja.
if git remote get-url origin >/dev/null 2>&1; then
  if ! git fetch --prune origin >/dev/null 2>&1; then
    echo "No se pudo consultar el remoto, y sin eso el número de la spec puede" >&2
    echo "repetir uno que otra persona ya tomó. Revisa tu conexión y repite." >&2
    echo "Si de verdad necesitas trabajar sin remoto, usa:" >&2
    echo "    SDD_SIN_REMOTO=1 bash scripts/nueva-spec.sh $1" >&2
    [ "${SDD_SIN_REMOTO:-0}" = "1" ] || exit 1
    echo "Aviso: continuando sin consultar el remoto, por SDD_SIN_REMOTO=1." >&2
  fi
fi

# Reúne los números ya tomados: carpetas de specs/, ramas (locales y del
# remoto, que ya quedaron actualizadas arriba) y specs que ya están en el main
# del remoto. Una rama integrada se borra (ver CONTRIBUTING.md), así que de
# esas specs no queda rama: solo su carpeta.
USADOS=""
for d in specs/[0-9][0-9][0-9]-*/; do
  [ -d "$d" ] || continue
  USADOS="$USADOS $(basename "$d" | cut -c1-3)"
done
for b in $(git branch -a --format='%(refname:short)' | grep -oE 'feature/[0-9]{3}' | cut -d/ -f2 || true); do
  USADOS="$USADOS $b"
done
for s in $(git ls-tree --name-only origin/main specs/ 2>/dev/null | sed -n 's|^specs/\([0-9][0-9][0-9]\)-.*|\1|p' || true); do
  USADOS="$USADOS $s"
done

esta_tomado() {
  for u in $USADOS; do
    [ "$((10#$u))" -eq "$((10#$1))" ] && return 0
  done
  return 1
}

if [ -n "${SDD_NUMERO:-}" ]; then
  # Número explícito. Hace falta porque el mapa reserva los números por
  # funcionalidad (sdd/mapa-funcionalidades.md) y no las construimos en orden:
  # sin esto, pedir la 007 cuando la más alta es la 004 crearía una "005".
  if ! echo "$SDD_NUMERO" | grep -qE '^[0-9]{3}$'; then
    echo "SDD_NUMERO debe ser exactamente tres dígitos, por ejemplo 007." >&2
    echo "Recibí: '$SDD_NUMERO'" >&2
    exit 1
  fi
  if esta_tomado "$SDD_NUMERO"; then
    echo "El número $SDD_NUMERO ya está tomado por una spec o una rama." >&2
    echo "Revisa sdd/mapa-funcionalidades.md y elige el que corresponde, o" >&2
    echo "deja que el script lo calcule solo (sin SDD_NUMERO)." >&2
    exit 1
  fi
  NUM="$SDD_NUMERO"
else
  # Sin número explícito: el siguiente al más alto que ya existe.
  ULTIMO=0
  for u in $USADOS; do
    n=$((10#$u)); [ "$n" -gt "$ULTIMO" ] && ULTIMO=$n
  done
  NUM=$(printf "%03d" $((ULTIMO + 1)))
fi

RAMA="feature/${NUM}-${NOMBRE}"
CARPETA="specs/${NUM}-${NOMBRE}"

git checkout main >/dev/null 2>&1
git pull --ff-only >/dev/null 2>&1 || echo "Aviso: no se pudo actualizar main desde el remoto (se continúa con la copia local)."
git checkout -b "$RAMA"

mkdir -p "$CARPETA"
sed -e "s/\[NNN\]/${NUM}/g" \
    -e "s/\[NNN-nombre-corto\]/${NUM}-${NOMBRE}/g" \
    -e "s/\[AAAA-MM-DD\]/$(date +%F)/g" \
    sdd/plantillas/spec.md > "$CARPETA/spec.md"

echo "Rama creada:   $RAMA"
echo "Spec creada:   $CARPETA/spec.md"
