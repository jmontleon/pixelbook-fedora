Name:       pixelbook-udev
Version:    1.0.0
Release:    1%{?dist}
License:    BSD
Summary:    udev rules for Pixelbook backlights
Source0:    99-pixelbook-backlights.rules 
BuildArch:  noarch

Requires: systemd-udev

%description
udev rules for Pixelbook backlights

%prep

%build

%install
mkdir -p %{buildroot}//usr/lib/udev/rules.d/
install -m 0755 %{SOURCE0} %{buildroot}/usr/lib/udev/rules.d/
%check

%files
/usr/lib/udev/rules.d/99-pixelbook-backlights.rules

%post
udevadm control --reload-rules
udevadm trigger

%postun
udevadm control --reload-rules

%changelog
* Sun Jul 25 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.0-1
- Initial build

