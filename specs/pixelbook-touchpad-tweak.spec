Name:       pixelbook-touchpad-tweak
Version:    1.0.0
Release:    1%{?dist}
License:    BSD
Summary:    xorg.conf.d file to tweak the Pixelbook touchpad
Source0:    99-pixelbook-touchpad-tweak.conf
BuildArch:  noarch

Requires: xorg-x11-server-Xorg

%description
xorg.conf.d file to tweak the Pixelbook touchpad

%prep

%build

%install
mkdir -p %{buildroot}/etc/X11/xorg.conf.d/
install -m 0664 %{SOURCE0} %{buildroot}/etc/X11/xorg.conf.d/
%check

%files
/etc/X11/xorg.conf.d/99-pixelbook-touchpad-tweak.conf

%changelog
* Sun Jul 25 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.0-1
- Initial build

