Name:       pixelbook-scripts
Version:    1.0.4
Release:    1%{?dist}
Summary:    Scripts for interacting with pixelbook backlights and touchpad
License:    WTFPL
Source0:    pixelbook-display-backlight
Source1:    pixelbook-keyboard-backlight
Source2:    pixelbook-touchscreen-click
Source3:    pixelbook-display-orientation
Source4:    pixelbook-disable-tablet-touchpad
BuildArch:  noarch

Requires: acpid
Requires: iio-sensor-proxy
Requires: inotify-tools
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
install -m 0755 %{SOURCE3} %{buildroot}%{_bindir}/
install -m 0755 %{SOURCE4} %{buildroot}%{_bindir}/
%check

%files
/usr/bin/*

%changelog
* Sun Aug 08 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.4-1
- Update orientation script to only monitor accel sensor

* Sat Aug 07 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.3-1
- Add script to control touchpad tablet mode
- Try to improve reliability of touchscreen click script

* Sat Aug 07 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.2-1
- Improve display orientation script

* Thu Aug 05 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.1-1
- Add display orientation script

* Sun Jul 25 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.0-2
- Fix touchscreen script name
- Add missing xinput dependency

* Sun Jul 25 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.0-1
- Initial build

