#!/usr/bin/env bash
# Calcula el número que le toca a la próxima spec, e imprime solo eso: NNN.
#
# Uso:
#   bash scripts/numero-de-spec.sh            # el siguiente al más alto que exista
#   SDD_NUMERO=007 bash scripts/numero-de-spec.sh   # valida un número reservado por el mapa
#
# Para qué sirve: SpecKit crea la rama y la carpeta de la spec, pero numera
# mirando únicamente las carpetas de `specs/` del checkout actual. Eso no basta
# aquí por dos razones:
#
#   1. El mapa (.specify/memory/mapa-funcionalidades.md) reserva los números por
#      funcionalidad y no las construimos en orden: pedir la 007 cuando la más
#      alta es la 004 daría una "005", que en el mapa es otra funcionalidad.
#   2. Trabajamos en paralelo y en varios worktrees. Un worktree no ve las
#      carpetas de specs que viven en la rama de otro, así que el número hay que
#      calcularlo contra el remoto, no contra el disco.
#
# El número que imprime se le pasa a SpecKit:
#   bash .specify/extensions/git/scripts/bash/create-new-feature-branch.sh \
#        --short-name <nombre> --number $(bash scripts/numero-de-spec.sh) "<descripción>"
set -euo pipefail

RAIZ=$(git rev-parse --show-toplevel)
cd "$RAIZ"

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
    echo "    SDD_SIN_REMOTO=1 bash scripts/numero-de-spec.sh" >&2
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
  if ! echo "$SDD_NUMERO" | grep -qE '^[0-9]{3}$'; then
    echo "SDD_NUMERO debe ser exactamente tres dígitos, por ejemplo 007." >&2
    echo "Recibí: '$SDD_NUMERO'" >&2
    exit 1
  fi
  if esta_tomado "$SDD_NUMERO"; then
    echo "El número $SDD_NUMERO ya está tomado por una spec o una rama." >&2
    echo "Revisa .specify/memory/mapa-funcionalidades.md y elige el que" >&2
    echo "corresponde, o deja que el script lo calcule solo (sin SDD_NUMERO)." >&2
    exit 1
  fi
  echo "$SDD_NUMERO"
else
  ULTIMO=0
  for u in $USADOS; do
    n=$((10#$u)); [ "$n" -gt "$ULTIMO" ] && ULTIMO=$n
  done
  printf "%03d\n" $((ULTIMO + 1))
fi
