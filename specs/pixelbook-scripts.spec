Name:       pixelbook-scripts
Version:    1.0.10
Release:    1%{?dist}
Summary:    Scripts for interacting with pixelbook backlights and touchpad
License:    WTFPL
Source0:    pixelbook-acpi.service
Source1:    pixelbook-keyboard-backlight
Source2:    pixelbook-touchscreen-click
Source3:    pixelbook-display-orientation
Source4:    pixelbook-acpi
Source5:    pixelbook-display-orientation.service
Source6:    pixelbook-touchscreen-click.service
Source7:    pixelbook-keyboard-backlight.service
BuildArch:  noarch

BuildRequires: systemd-rpm-macros

Requires: acpid
Requires: kbd
Requires: iio-sensor-proxy
Requires: inotify-tools
Requires: python3-pynput
Requires: xinput

%description
Scripts for interacting with pixelbook backlights and touchpad

%prep

%build

%install
mkdir -p %{buildroot}%{_libexecdir}
mkdir -p %{buildroot}%{_userunitdir}
install -m 0644 %{SOURCE0} %{buildroot}%{_userunitdir}/
install -m 0755 %{SOURCE1} %{buildroot}%{_libexecdir}/
install -m 0755 %{SOURCE2} %{buildroot}%{_libexecdir}/
install -m 0755 %{SOURCE3} %{buildroot}%{_libexecdir}/
install -m 0755 %{SOURCE4} %{buildroot}%{_libexecdir}/
install -m 0644 %{SOURCE5} %{buildroot}%{_userunitdir}/
install -m 0644 %{SOURCE6} %{buildroot}%{_userunitdir}/
install -m 0644 %{SOURCE7} %{buildroot}%{_userunitdir}/
%check

%post
%systemd_user_post pixelbook-acpi.service
%systemd_user_post pixelbook-display-orientation.service
%systemd_user_post pixelbook-touchscreen-click.service
%systemd_user_post pixelbook-keyboard-backlight.service

%preun
%systemd_user_preun pixelbook-acpi.service
%systemd_user_preun pixelbook-display-orientation.service
%systemd_user_preun pixelbook-touchscreen-click.service
%systemd_user_preun pixelbook-keyboard-backlight.service

%postun
%systemd_user_postun pixelbook-acpi.service
%systemd_user_postun pixelbook-display-orientation.service
%systemd_user_postun pixelbook-touchscreen-click.service
%systemd_user_postun pixelbook-keyboard-backlight.service

%files
/%{_libexecdir}/*
/%{_userunitdir}/*

%changelog
* Sun Nov 17 2024 Jason Montleon <jmontleo@redhat.com> - 1.0.10-1
- Update acpi script to work better with multiple users

* Wed Oct 16 2024 Jason Montleon <jmontleo@redhat.com> - 1.0.9-1
- Rewrite pixelbook-keyboard-backlight using only evdev for python 3.13

* Tue Aug 02 2022 Jason Montleon <jmontleo@redhat.com> - 1.0.8-1
- Stop keyboard backlight service from failing

* Wed May 18 2022 Jason Montleon <jmontleo@redhat.com> - 1.0.7-1
- Implement jack detection workaround using ACPI
- Start running scripts with user systemd services

* Wed Jan 05 2022 Huy Le <dacrazyazn@gmail.com> - 1.0.6-1
- Add stylus/pen to be included in display orientation change

* Mon Dec 20 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.5-1
- Fix duplicate source, add pixelbook-disable-tablet-touchpad

* Sun Aug 08 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.4-1
- Update orientation script to only monitor accel sensor

* Sat Aug 07 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.3-1
- Add script to control touchpad tablet mode
- Try to improve reliability of touchscreen click script

* Sat Aug 07 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.2-1
- Improve display orientation script

* Thu Aug 05 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.1-1
- Add display orientation script

* Sun Jul 25 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.0-2
- Fix touchscreen script name
- Add missing xinput dependency

* Sun Jul 25 2021 Jason Montleon <jmontleo@redhat.com> - 1.0.0-1
- Initial build

