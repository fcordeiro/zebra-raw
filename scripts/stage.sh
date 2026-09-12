#!/bin/sh
# Instala somente no diretório de staging fornecido, sem tocar no sistema.
set -eu
[ "$#" -eq 1 ] && [ -n "$1" ] && [ "$1" != / ] || { echo 'Uso: stage.sh DIRETORIO_DE_STAGING' >&2; exit 2; }
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
dest=$1
install -d "$dest/usr/share/zebra-raw" "$dest/usr/bin" "$dest/usr/share/applications" "$dest/usr/share/doc/zebra-raw" "$dest/usr/share/icons/hicolor/scalable/apps" "$dest/usr/share/metainfo"
install -m 644 "$root/core.py" "$root/zebra.py" "$root/VERSION" "$dest/usr/share/zebra-raw/"
install -m 755 "$root/packaging/zebra-raw" "$dest/usr/bin/zebra-raw"
install -d "$dest/usr/share/zebra-raw/icons"
install -m 644 "$root/io.github.fcordeiro.zebraraw.desktop" "$dest/usr/share/applications/"
install -m 644 "$root/icons/zebra-raw.svg" "$dest/usr/share/zebra-raw/icons/"
install -m 644 "$root/icons/zebra-raw.svg" "$dest/usr/share/icons/hicolor/scalable/apps/io.github.fcordeiro.zebraraw.svg"
install -m 644 "$root/io.github.fcordeiro.zebraraw.metainfo.xml" "$dest/usr/share/metainfo/"
install -m 644 "$root/README.md" "$dest/usr/share/doc/zebra-raw/"
