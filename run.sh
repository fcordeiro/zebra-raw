#!/bin/sh
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd) || exit 1
cd "$root" || exit 1
# Permite ao Wayland associar esta execução de desenvolvimento ao lançador e ícone.
export XDG_DATA_DIRS="$root/data${XDG_DATA_DIRS:+:$XDG_DATA_DIRS}"
exec /usr/bin/python3 zebra.py "$@"
