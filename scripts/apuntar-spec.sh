#!/usr/bin/env bash
# Escribe .specify/feature.json, el puntero que Spec Kit usa para saber en qué
# spec está trabajando este checkout.
#
# Uso:
#   bash scripts/apuntar-spec.sh          # deduce la spec de la rama actual
#   bash scripts/apuntar-spec.sh 002      # apunta a specs/002-...
#
# Cuándo hace falta:
#
#   - En las specs creadas antes de adoptar Spec Kit (001 a 007): nacieron con
#     el script anterior, que no escribía este archivo.
#   - En cada worktree nuevo: feature.json es estado por checkout y está en
#     .specify/.gitignore, así que no viaja de un worktree a otro.
#
# /speckit-specify lo escribe solo, así que para las specs que vengan de aquí
# en adelante este script no se necesita.
set -euo pipefail

RAIZ=$(git rev-parse --show-toplevel)
cd "$RAIZ"

if [ $# -ge 1 ] && [ -n "${1:-}" ]; then
  BUSCA="$1"
else
  # De la rama feature/NNN-nombre sale el NNN. El directorio de la spec no
  # lleva el prefijo "feature/", y por eso Spec Kit no lo deduce solo.
  RAMA=$(git branch --show-current)
  BUSCA=$(echo "${RAMA#feature/}" | cut -c1-3)
  if ! echo "$BUSCA" | grep -qE '^[0-9]{3}$'; then
    echo "La rama '$RAMA' no es feature/NNN-nombre, así que no puedo deducir la spec." >&2
    echo "Pasa el número: bash scripts/apuntar-spec.sh 002" >&2
    exit 1
  fi
fi

CARPETA=""
for d in specs/"$BUSCA"-*/; do
  [ -d "$d" ] && CARPETA="${d%/}" && break
done

if [ -z "$CARPETA" ]; then
  echo "No existe ninguna carpeta specs/$BUSCA-… en esta rama." >&2
  exit 1
fi

mkdir -p .specify
printf '{"feature_directory":"%s"}\n' "$CARPETA" > .specify/feature.json

echo "Spec Kit ahora apunta a: $CARPETA"
