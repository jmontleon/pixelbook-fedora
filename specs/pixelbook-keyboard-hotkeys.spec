Name:       pixelbook-keyboard-hotkeys
Version:    1.0.0
Release:    1%{?dist}
License:    GPL 2
Summary:    Keyboard Hotkey Tweaks for Pixelbook
Source0:    61-eve-keyboard.hwdb
BuildArch:  noarch

Requires: systemd-udev

%description
Keyboard Hotkey Tweaks for Pixelbook

%prep

%build

%install
mkdir -p %{buildroot}/usr/lib/udev/hwdb.d
install -m 0664 %{SOURCE0} %{buildroot}/usr/lib/udev/hwdb.d
%check

%post
systemd-hwdb update
udevadm trigger

%postun
systemd-hwdb update

%files
/usr/lib/udev/hwdb.d/61-eve-keyboard.hwdb

%changelog
* Sun Jul 25 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.0-1
- Initial build
