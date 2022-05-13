%global library pynput
%global py3 python3
%global py3dev python3

Name:       python-%{library}
Version:    1.7.6
Release:    1%{?dist}
Summary:    This library allows you to control and monitor input devices.
License:    GPL 3.0
URL:        https://github.com/moses-palmer/pynput
Source0:    https://github.com/moses-palmer/pynput/archive/refs/tags/v%{version}.tar.gz
BuildArch:  noarch

%package -n %{py3}-%{library}
Summary: This library allows you to control and monitor input devices.
BuildRequires: %{py3dev}-devel
BuildRequires: %{py3dev}-pip
BuildRequires: %{py3dev}-rpm-macros
BuildRequires: %{py3}-setuptools
BuildRequires: %{py3}-setuptools-lint
BuildRequires: %{py3}-sphinx
BuildRequires: %{py3}-wheel

Requires: %{py3}
Requires: %{py3}-evdev >= 1.3
Requires: %{py3}-wheel

%description -n %{py3}-%{library}
This library allows you to control and monitor input devices.

%package doc
Summary: Documentation for %{name}.
%description doc
%{summary}

%description
This library allows you to control and monitor input devices.

%prep
%autosetup -n %{library}-%{version}

%build
%py3_build

sphinx-build-3 docs/ html
%{__rm} -rf html/.buildinfo
%{__rm} -rf html/.doctrees

%install
%py3_install

%check

%files -n %{py3}-%{library}
%{python3_sitelib}/%{library}
%{python3_sitelib}/%{library}-*.egg-info

%files doc
%doc html

%changelog
* Thu May 12 2022 Jason Montleon <jmontleo@redhat.com> - 1.7.6-1
- Update to 1.7.6

* Sat Jul 24 2021 Jason Montleon <jmontleo@redhat.com> - 1.7.3-3
- Add missing setuptools-lint build-dep

* Sat Jul 24 2021 Jason Montleon <jmontleo@redhat.com> - 1.7.3-2
- Add missing pip build-dep

* Sat Jul 24 2021 Jason Montleon <jmontleo@redhat.com> - 1.7.3-1
- Initial Build
