Name:           mdapi
Version:        2.2.2
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
BuildRequires:  python3-devel
BuildRequires:  systemd

Requires:  python3-aiohttp
Requires:  python3-requests
Requires:  python3-setuptools
Requires:  python3-simplejson
Requires:  python3-sqlalchemy
Requires:  python3-werkzeug

Requires(post):     systemd
Requires(preun):    systemd
Requires(postun):   systemd


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
* Mon Nov 23 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.2.2-1
- Update to 2.2.2
- Fix accessing the configuration to adjust the link on the front page

* Sun Nov 22 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.2.1-1
- Update to 2.2.1
- Fix the links in the front page with it's accessed without trailing slash
  (Patrick Uiterwijk)

* Thu Nov 19 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.2-1
- Update to 2.2
- Fix typo in the cron job

* Thu Nov 19 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.1-1
- Update to 2.1
- Drop un-used import
- Fix prettifying the JSON only on demand

* Thu Nov 19 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.0-1
- Update to 2.0
- Fix typos on the front page
- Add the dependencies (Requires, Obsoletes, Provides, Conflicts, Enhances,
  Recommends, Suggests, Supplements) to the JSON returned
- Add the option to return a prettier JSON
- Add the possibility to disable checking the SSL cert

* Tue Nov 10 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 1.2.2-1
- Update to 1.2.2
- Be consistent about providing links on the front page

* Tue Nov 10 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 1.2.1-1
- Update to 1.2.1
- Fix typo in the routing

* Tue Nov 10 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 1.2-1
- Update 1.2
- Add the possibility to prefix the URLs at which mdapi answers
- Simplify the routing by listing them
- Fix the example and link in the documentation on the front page

* Tue Nov 10 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 1.1-1
- Update to 1.1
- Make the URLs to pkgdb, the koji repo and the download server configurable for
  the cron job

* Mon Nov 09 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 1.0-1
- Update to 1.0

* Tue Oct 27 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 0.1-1
- First package for Fedora
