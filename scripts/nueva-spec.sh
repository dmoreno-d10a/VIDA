#!/usr/bin/env bash
# Crea una nueva especificación SDD: rama feature/NNN-nombre + carpeta specs/NNN-nombre/
# Uso: bash scripts/nueva-spec.sh <nombre-corto-en-kebab-case>
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

# Calcula el siguiente número a partir de specs/ y de las ramas existentes
# (locales y del remoto, que ya quedaron actualizadas arriba).
ULTIMO=0
for d in specs/[0-9][0-9][0-9]-*/; do
  [ -d "$d" ] || continue
  n=$(basename "$d" | cut -c1-3); n=$((10#$n))
  [ "$n" -gt "$ULTIMO" ] && ULTIMO=$n
done
for b in $(git branch -a --format='%(refname:short)' | grep -oE 'feature/[0-9]{3}' | cut -d/ -f2 || true); do
  n=$((10#$b)); [ "$n" -gt "$ULTIMO" ] && ULTIMO=$n
done
# Y las specs que ya están en el main del remoto. Una rama integrada se borra
# (ver CONTRIBUTING.md), así que de esas specs no queda rama: solo su carpeta.
for s in $(git ls-tree --name-only origin/main specs/ 2>/dev/null | sed -n 's|^specs/\([0-9][0-9][0-9]\)-.*|\1|p' || true); do
  n=$((10#$s)); [ "$n" -gt "$ULTIMO" ] && ULTIMO=$n
done
NUM=$(printf "%03d" $((ULTIMO + 1)))

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
