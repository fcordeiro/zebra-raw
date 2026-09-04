Name:           zebra-raw
Version:        1.0.0
Release:        1
Summary:        GTK utility for RAW ZPL printing on Zebra GC420t USB
License:        LicenseRef-Proprietary
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
%dir %{_datadir}/doc/zebra-raw
%{_datadir}/doc/zebra-raw/README.md
