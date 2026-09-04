#!/bin/sh
set -eu
[ "$(id -u)" -eq 0 ] || { echo "Execute: sudo sh $0" >&2; exit 1; }
. /etc/os-release
case "$ID" in opensuse*) ;; *) echo 'Este instalador exige openSUSE.' >&2; exit 1;; esac
root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
zypper --non-interactive install rpm-build tar gzip
"$root/scripts/build-rpm.sh"
# O pacote foi gerado localmente e não tem assinatura. Não desabilita GPG nos repositórios.
zypper --non-interactive install --allow-unsigned-rpm "$root/dist/zebra-raw-$(cat "$root/VERSION")-1.noarch.rpm"
echo 'Instalado. Abra Zebra RAW pelo menu ou execute zebra-raw como usuário normal.'
echo 'Configure a fila USB no CUPS caso ainda não exista. Nenhuma impressão foi enviada.'
