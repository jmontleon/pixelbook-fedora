Name:       pixelbook-wireplumber
Version:    1.0.0
Release:    1%{?dist}
License:    MIT
Summary:    Wireplumber config for the Pixelbooks kbl_r5514_5663_max
Source0:    50-alsa-config.conf
BuildArch:  noarch

Requires: wireplumber

%description
Wireplumber config for the Pixelbooks kbl_r5514_5663_max

%prep

%build

%install
mkdir -p %{buildroot}/etc/wireplumber/wireplumber.conf.d/
install -m 0644 %{SOURCE0} %{buildroot}/etc/wireplumber/wireplumber.conf.d/

%check

%files
/etc/wireplumber/wireplumber.conf.d/50-alsa-config.conf

%changelog
* Sun Nov 17 2024 Daniel Brackenbury <daniel.brackenbury@gmail.com> - 1.0.1-1
- Update configuration for Wireplumber 0.5.5

* Fri Mar 31 2023 Jason Montleon <jmontleo@redhat.com> - 1.0.0-1
- Initial Build
