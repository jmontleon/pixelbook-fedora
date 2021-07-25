Name:       pixelbook-alsa-ucm
Version:    1.0.0
Release:    2%{?dist}
License:    BSD
Summary:    Alsa UCM profile for the Pixelbook
Source0:    HiFi.conf
Source1:    kbl-r5514-5663-.conf
BuildArch:  noarch

Requires: alsa-ucm

%description
Alsa UCM profile for the Pixelbook

%prep

%build

%install
mkdir -p %{buildroot}/usr/share/alsa/ucm2/kbl-r5514-5663-/
install -m 0755 %{SOURCE0} %{buildroot}/usr/share/alsa/ucm2/kbl-r5514-5663-/
install -m 0755 %{SOURCE1} %{buildroot}/usr/share/alsa/ucm2/kbl-r5514-5663-/
%check

%files
%dir /usr/share/alsa/ucm2/kbl-r5514-5663-/
/usr/share/alsa/ucm2/kbl-r5514-5663-/*

%changelog
* Sun Jul 25 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.0-2
- Fix description

* Sun Jul 25 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.0-1
- Initial build

