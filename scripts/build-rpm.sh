#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
version=$(cat "$root/VERSION")
command -v rpmbuild >/dev/null || { echo 'Instale rpm-build para gerar o .rpm.' >&2; exit 1; }
stage=$(mktemp -d)
trap 'rm -rf "$stage"' EXIT HUP INT TERM
mkdir -p "$stage/SOURCES" "$stage/BUILD" "$stage/RPMS" "$stage/SPECS" "$stage/SRPMS" "$stage/zebra-raw-$version" "$root/dist"
for file in core.py zebra.py VERSION README.md zebra-raw.desktop scripts/stage.sh packaging/zebra-raw; do
    install -D -m 644 "$root/$file" "$stage/zebra-raw-$version/$file"
done
chmod 755 "$stage/zebra-raw-$version/scripts/stage.sh"
tar -C "$stage" -czf "$stage/SOURCES/zebra-raw-$version.tar.gz" "zebra-raw-$version"
sed "s/^Version:.*/Version:        $version/" "$root/packaging/zebra-raw.spec" > "$stage/SPECS/zebra-raw.spec"
rpmbuild --define "_topdir $stage" --define '_build_id_links none' -bb "$stage/SPECS/zebra-raw.spec"
cp "$stage/RPMS/noarch/"*.rpm "$root/dist/"
