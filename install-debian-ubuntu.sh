#!/bin/sh
# Execute a partir da cópia completa do projeto.
set -eu
[ "$(id -u)" -eq 0 ] || { echo "Execute: sudo sh $0" >&2; exit 1; }
. /etc/os-release
case " $ID ${ID_LIKE:-} " in *debian*|*ubuntu*) ;; *) echo 'Este instalador exige Debian/Ubuntu.' >&2; exit 1;; esac
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
apt-get update
apt-get install -y dpkg-dev
"$root/scripts/build-deb.sh"
apt-get install -y "$root/dist/zebra-raw_$(cat "$root/VERSION")_all.deb"
echo 'Instalado. Abra Zebra RAW pelo menu ou execute zebra-raw como usuário normal.'
echo 'Configure a fila USB no CUPS caso ainda não exista. Nenhuma impressão foi enviada.'
