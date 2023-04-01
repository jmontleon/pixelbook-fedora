Name:       pixelbook-wireplumber
Version:    1.0.0
Release:    1%{?dist}
License:    MIT
Summary:    Wireplumber config for the Pixelbooks kbl_r5514_5663_max
Source0:    50-alsa-config.lua
BuildArch:  noarch

Requires: wireplumber

%description
Wireplumber config for the Pixelbooks kbl_r5514_5663_max

%prep

%build

%install
mkdir -p %{buildroot}/etc/wireplumber/main.lua.d/
install -m 0644 %{SOURCE0} %{buildroot}/etc/wireplumber/main.lua.d/

%check

%files
/etc/wireplumber/main.lua.d/50-alsa-config.lua

%changelog
* Fri Mar 31 2023 Jason Montleon <jmontleo@redhat.com> - 1.0.0-1
- Initial Build
