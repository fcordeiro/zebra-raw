#!/bin/sh
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd) || exit 1
cd "$root" || exit 1
# Registra os recursos de desenvolvimento no local padrão do usuário.  No
# Plasma/Wayland a barra de tarefas é outro processo: ela só associa o
# aplicativo ao ícone se encontrar o .desktop no próprio banco de dados dela.
data_home=${XDG_DATA_HOME:-"$HOME/.local/share"}
install -D -m 644 "$root/data/applications/io.github.fcordeiro.zebraraw.desktop" \
  "$data_home/applications/io.github.fcordeiro.zebraraw.desktop"
install -D -m 644 "$root/data/icons/hicolor/scalable/apps/io.github.fcordeiro.zebraraw.svg" \
  "$data_home/icons/hicolor/scalable/apps/io.github.fcordeiro.zebraraw.svg"
export XDG_DATA_DIRS="$root/data${XDG_DATA_DIRS:+:$XDG_DATA_DIRS}"
exec /usr/bin/python3 zebra.py "$@"
