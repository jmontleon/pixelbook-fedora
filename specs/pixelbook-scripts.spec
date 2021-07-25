Name:       pixelbook-scripts
Version:    1.0.0
Release:    2%{?dist}
Summary:    Scripts for interacting with pixelbook backlights and touchpad
License:    WTFPL
Source0:    pixelbook-display-backlight
Source1:    pixelbook-keyboard-backlight
Source2:    pixelbook-touchscreen-click
BuildArch:  noarch

Requires: python3-pynput
Requires: xinput

%description
Scripts for interacting with pixelbook backlights and touchpad

%prep

%build

%install
mkdir -p %{buildroot}%{_bindir}
install -m 0755 %{SOURCE0} %{buildroot}%{_bindir}/
install -m 0755 %{SOURCE1} %{buildroot}%{_bindir}/
install -m 0755 %{SOURCE2} %{buildroot}%{_bindir}/
%check

%files
/usr/bin/*

%changelog
* Sun Jul 25 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.0-2
- Fix touchscreen script name
- Add missing xinput dependency

* Sun Jul 25 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.0-1
- Initial build

