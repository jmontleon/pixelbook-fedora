Name:       pixelbook-aer
Version:    1.0.0
Release:    1%{?dist}
Summary:    Fix for Pixelbook's excessive AER logging
License:    WTFPL
Source0:    pixelbook-aer.service
BuildArch:  noarch
BuildRequires: systemd-rpm-macros
Requires: pciutils

%description
Fix for Pixelbook's excessive AER logging

%prep

%build

%install
mkdir -p %{buildroot}%{_unitdir}
install -m 0644 %{SOURCE0} %{buildroot}%{_unitdir}/
%check

%post
%systemd_post pixelbook-aer.service

%preun
%systemd_preun pixelbook-aer.service

%postun
%systemd_postun_with_restart pixelbook-aer.service

%files
%{_unitdir}/pixelbook-aer.service

%changelog
* Mon Mar 14 2022 Jason Montleon <jason@montleon.com> - 1.0.0-1
- Initial Build
