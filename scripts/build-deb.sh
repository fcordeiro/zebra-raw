#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
version=$(cat "$root/VERSION")
command -v dpkg-deb >/dev/null || { echo 'Instale dpkg-dev para gerar o .deb.' >&2; exit 1; }
stage=$(mktemp -d)
trap 'rm -rf "$stage"; rm -f "$stage.deb"' EXIT HUP INT TERM
"$root/scripts/stage.sh" "$stage"
install -d "$stage/DEBIAN" "$root/dist"
cat > "$stage/DEBIAN/control" <<CONTROL
Package: zebra-raw
Version: $version
Section: utils
Priority: optional
Architecture: all
Maintainer: Zebra RAW maintainers <5787523+fcordeiro@users.noreply.github.com>
Depends: python3 (>= 3.8), python3-gi, gir1.2-gtk-3.0, cups-client
Recommends: cups
Description: Interface GTK para envio ZPL RAW a Zebra GC420t USB
 Envia arquivos ZPL sem filtros pelo CUPS, com perfis de midia,
 configuracao termica, calibracao e consulta da fila.
CONTROL
dpkg-deb --root-owner-group --build "$stage" "$stage.deb"
mv "$stage.deb" "$root/dist/zebra-raw_${version}_all.deb"
