Name:       pixelbook-touchpad-service
Version:    1.0.0
Release:    1%{?dist}
Summary:    Service to workaround mouse failures on reboot
License:    WTFPL
Source0:    pixelbook-touchpad.service
BuildArch:  noarch
BuildRequires: systemd-rpm-macros
Requires: pciutils

%description
Service to workaround mouse failures on reboot

%prep

%build

%install
mkdir -p %{buildroot}%{_unitdir}
install -m 0644 %{SOURCE0} %{buildroot}%{_unitdir}/
%check

%post
%systemd_post pixelbook-touchpad.service

%preun
%systemd_preun pixelbook-touchpad.service

%postun
%systemd_postun_with_restart pixelbook-touchpad.service

%files
%{_unitdir}/pixelbook-touchpad.service

%changelog
* Mon Mar 14 2022 Jason Montleon <jason@montleon.com> - 1.0.0-1
- Initial Build
