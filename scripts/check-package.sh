#!/bin/sh
set -eu
python3 -m unittest discover -s tests -v
desktop-file-validate /usr/share/applications/zebra-raw.desktop
# DISPLAY isolado: não acessa a sessão gráfica nem a impressora do usuário.
Xvfb :97 -screen 0 1024x768x24 >/tmp/zebra-xvfb.log 2>&1 &
xvfb_pid=$!
trap 'kill "$xvfb_pid" 2>/dev/null || true' EXIT HUP INT TERM
sleep 1
DISPLAY=:97 python3 tests/smoke_gui.py
