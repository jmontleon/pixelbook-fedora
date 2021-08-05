Name:       pixelbook-udev
Version:    1.0.1
Release:    1%{?dist}
License:    BSD
Summary:    udev rules for Pixelbook backlights, sensors, and keyboard
Source0:    99-pixelbook-backlights.rules 
Source1:    61-eve-sensor.hwdb
Source2:    61-eve-keyboard.hwdb
BuildArch:  noarch

Requires: systemd-udev

Obsoletes: pixelbook-keyboard

%description
udev rules for Pixelbook backlights, sensors, and keyboard.

%prep

%build

%install
mkdir -p %{buildroot}/usr/lib/udev/rules.d/
mkdir -p %{buildroot}/usr/lib/udev/hwdb.d/
install -m 0755 %{SOURCE0} %{buildroot}/usr/lib/udev/rules.d/
install -m 0664 %{SOURCE1} %{buildroot}/usr/lib/udev/hwdb.d/
install -m 0664 %{SOURCE2} %{buildroot}/usr/lib/udev/hwdb.d/
%check

%files
/usr/lib/udev/rules.d/99-pixelbook-backlights.rules
/usr/lib/udev/hwdb.d/61-eve-sensor.hwdb
/usr/lib/udev/hwdb.d/61-eve-keyboard.hwdb

%post
systemd-hwdb update
udevadm control --reload-rules
udevadm trigger

%postun
systemd-hwdb update
udevadm control --reload-rules

%changelog
* Thu Aug 05 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.1-1
- Add sensor hwdb config
- Move keyboard udev rule here and obsolete package

* Sun Jul 25 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.0-1
- Initial build

