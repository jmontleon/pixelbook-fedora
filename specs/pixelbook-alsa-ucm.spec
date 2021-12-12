Name:       pixelbook-alsa-ucm
Version:    1.0.0
Release:    4%{?dist}
License:    BSD
Summary:    Alsa UCM profile for the Pixelbook
Source0:    HiFi.conf
Source1:    kbl-r5514-5663-.conf
BuildArch:  noarch

Requires: alsa-ucm >= 1.2.6

%description
Alsa UCM profile for the Pixelbook

%prep

%build

%install
mkdir -p %{buildroot}/usr/share/alsa/ucm2/conf.d/kbl-r5514-5663-/
install -m 0755 %{SOURCE0} %{buildroot}/usr/share/alsa/ucm2/conf.d/kbl-r5514-5663-/
install -m 0755 %{SOURCE1} %{buildroot}/usr/share/alsa/ucm2/conf.d/kbl-r5514-5663-/
%check

%files
%dir /usr/share/alsa/ucm2/conf.d/kbl-r5514-5663-/
/usr/share/alsa/ucm2/conf.d/kbl-r5514-5663-/*

%changelog
* Sun Dec 12 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.0-4
- Move configs into conf.d directory for alsa 1.2.6 compatibility

* Wed Jul 28 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.0-3
- Reduce the Syntax level to 3 for unupdated F34 systems.

* Sun Jul 25 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.0-2
- Fix description

* Sun Jul 25 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.0-1
- Initial build

