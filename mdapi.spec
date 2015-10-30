Name:           mdapi
Version:        0.1
Release:        1%{?dist}
Summary:        A simple API to query the metadata of the repositories

License:        GPLv2+
URL:            https://pagure.io/mdapi
Source0:        https://pagure.io/releases/mdapi/%{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-aiohttp
BuildRequires:  python3-requests
BuildRequires:  python3-setuptools
BuildRequires:  python3-simplejson
BuildRequires:  python3-sqlalchemy
BuildRequires:  python3-werkzeug

Requires:  python3-aiohttp
Requires:  python3-requests
Requires:  python3-setuptools
Requires:  python3-simplejson
Requires:  python3-sqlalchemy
Requires:  python3-werkzeug

%description
Small web and asynchronous application serving the metadata of the Fedora
repositories


%prep
%setup -q

%build
%{__python3} setup.py build


%install
%{__python3} setup.py install -O1 --skip-build --root=%{buildroot}

# Install the systemd service file
mkdir -p $RPM_BUILD_ROOT/%{_unitdir}
install -m 644 mdapi.service $RPM_BUILD_ROOT/%{_unitdir}/mdapi.service


%post
%systemd_post mdapi.service

%preun
%systemd_preun mdapi.service

%postun
%systemd_postun_with_restart mdapi.service


%files
%doc COPYING
%{python3_sitelib}/mdapi/
%{python3_sitelib}/mdapi*.egg-info
%{_bindir}/mdapi-get_repo_md
%{_bindir}/mdapi-run
%{_unitdir}/mdapi.service


%changelog
* Tue Oct 27 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1-1
- First package for Fedora
