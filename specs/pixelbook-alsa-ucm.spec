Name:       pixelbook-alsa-ucm
Version:    1.0.0
Release:    5%{?dist}
License:    BSD
Summary:    Alsa UCM profile for the Pixelbook
Source0:    HiFi.conf
Source1:    kbl-r5514-5663-.conf
BuildArch:  noarch

Requires: alsa-ucm >= 1.2.7

%description
Alsa UCM profile for the Pixelbook

%prep

%build

%install
mkdir -p %{buildroot}/usr/share/alsa/ucm2/Intel/kbl-r5514-5663-/
mkdir -p %{buildroot}/usr/share/alsa/ucm2/conf.d/kbl-r5514-5663-/
install -m 0755 %{SOURCE0} %{buildroot}/usr/share/alsa/ucm2/Intel/kbl-r5514-5663-/
install -m 0755 %{SOURCE1} %{buildroot}/usr/share/alsa/ucm2/Intel/kbl-r5514-5663-/
cd %{buildroot}/usr/share/alsa/ucm2/conf.d/kbl-r5514-5663-/
ln -sf ../../Intel/kbl-r5514-5663-/kbl-r5514-5663-.conf 
%check

%files
%dir /usr/share/alsa/ucm2/conf.d/kbl-r5514-5663-/
%dir /usr/share/alsa/ucm2/Intel/kbl-r5514-5663-/
/usr/share/alsa/ucm2/conf.d/kbl-r5514-5663-/*
/usr/share/alsa/ucm2/Intel/kbl-r5514-5663-/*

%changelog
* Sat Jun 04 2022 Jason Montleon <jmontleo@redhat.com> - 1.0.0-5
- Adjust configuration file locations for alsa 1.2.7 compatibility

* Sun Dec 12 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.0-4
- Move configs into conf.d directory for alsa 1.2.6 compatibility

* Wed Jul 28 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.0-3
- Reduce the Syntax level to 3 for unupdated F34 systems.

* Sun Jul 25 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.0-2
- Fix description

* Sun Jul 25 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.0-1
- Initial build

