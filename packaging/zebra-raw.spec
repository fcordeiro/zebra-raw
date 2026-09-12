Name:           zebra-raw
Version:        1.2.1
Release:        1
Summary:        GTK utility for RAW ZPL printing on Zebra thermal printers
License:        LicenseRef-Proprietary
Vendor:          Fernando J. Cordeiro
Packager:        Fernando J. Cordeiro <5787523+fcordeiro@users.noreply.github.com>
URL:            https://github.com/fcordeiro/zebra-raw
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
Requires:       /usr/bin/python3
Requires:       python3dist(pygobject)
Requires:       typelib-1_0-Gtk-3_0
Requires:       cups-client
Recommends:     cups

%description
Portuguese GTK interface for RAW ZPL printing through CUPS, with media
profiles, thermal settings, calibration and queue inspection.

%prep
%setup -q

%build

%install
./scripts/stage.sh %{buildroot}

%files
%dir %{_datadir}/zebra-raw
%{_datadir}/zebra-raw/*
%{_bindir}/zebra-raw
%{_datadir}/applications/zebra-raw.desktop
%{_datadir}/icons/hicolor/scalable/apps/zebra-raw.svg
%{_datadir}/metainfo/io.github.fcordeiro.ZebraRaw.metainfo.xml
%dir %{_datadir}/doc/zebra-raw
%{_datadir}/doc/zebra-raw/README.md
