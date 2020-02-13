Name:           mdapi
Version:        2.10.5
Release:        1%{?dist}
Summary:        A simple API to query the metadata of the repositories

License:        GPLv2+
URL:            https://pagure.io/mdapi
Source0:        https://pagure.io/releases/mdapi/%{name}-%{version}.tar.gz

BuildArch:      noarch

BuildRequires:  python3-aiohttp
BuildRequires:  python3-aiosqlite
BuildRequires:  python3-requests
BuildRequires:  python3-setuptools
BuildRequires:  python3-werkzeug
BuildRequires:  python3-devel
BuildRequires:  systemd

Requires:  python3-aiohttp
Requires:  python3-aiosqlite
Requires:  python3-multidict
Requires:  python3-requests
Requires:  python3-setuptools
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
* Fri Feb 09 2018 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.10.5-1
- Update to 2.10.5
- Fix the srcpkg endpoint by making it search for a direct match before trying
  the sub-packages

* Fri Feb 09 2018 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.10.4-1
- Update to 2.10.4
- Fix the content_type header on JSONP output

* Wed Jan 10 2018 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.10.3-1
- Update to 2.10.3
- Always initialize the output variable
- Fix getting package by their source name

* Tue Aug 08 2017 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.10.2-1
- Update to 2.10.2
- Fix importing MultiDict from multidict instead of aiohttp

* Tue Aug 08 2017 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.10.1-1
- Update to 2.10.1
- Fix the srcpkg endpoints

* Wed Aug 02 2017 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.10-1
- Update to 2.10
- Fix displaying the proper basename
- Expose the upstream URL as present in the metadata in the JSON returned
- Fix the JSONP support of the branches endpoint

* Wed Jul 12 2017 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.9-1
- Update to 2.9
- Add JSONP support to the application for easier integration with other apps

* Tue May 02 2017 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.8-1
- Update to 2.8
- Fix and improve the README
- Set the content_type and charset of the index page
- Download the source repository metadata as src_<name> and expose them
- Order the list of branches returned

* Mon Sep 12 2016 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.7-1
- Update to 2.7
- Add the possibility to query package by the name of their source package
- Return flags (Igor Gnatenko)
- Fix querying packages by their source package name (Igor Gnatenko)

* Thu May 12 2016 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.6-1
- Update to 2.6
- Fix get_repo_md to handle gzip correctly (Patrick Uiterwijk)
- Let the mdapi web app to return JSON with the correct mimetype (Patrick
  Uiterwijk)
- Adjust get_repo_md for the new URL structure on the mirrors

* Wed Mar 02 2016 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.5-1
- Update to 2.5
- Chain the method as coroutines making the process more asynchronous and a
  little bit faster
- Streamline the fedmsg diff publication to reduce the amount of data sent per
  message (especially for new repo where the diff concerns all the packages)

* Mon Feb 29 2016 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.4-1
- Update to 2.4
- Adjust copyright year
- Expand mdapi to return dependencies information (conflicts, enhances,
  recommends, suggests, supplements, requires, provides and obsoletes)
- Improve the cron script to retry after 30 seconds waiting, 3 times max if it
  fails to get info for a repo

* Wed Jan 13 2016 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.3-1
- Update to 2.3
- Return pretty JSON when the accept header is text/html (Till Maas)
- Order packages by their Epoch-Version-Release and return only the most recent
- Mention deployment URL in the README
- Adjust the JSON key from `files` to `changelogs` to reflect the content
- Rely on urllib and aiohttp.MultiDict to do the url arguments parsing
- Fix using ?pretty=False in a browser
- Drop the dependency on simplejson

* Tue Nov 24 2015 Pierre-Yves Chibon <pingou@pingoured.fr> - 2.2.3-1
- Update to 2.2.3
- Fix the branches endpoint (un-instantiated variable)

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
