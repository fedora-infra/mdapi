"""
mdapi
Copyright (C) 2015-2022 Red Hat, Inc.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Any Red Hat trademarks that are incorporated in the source
code or documentation are not subject to the GNU General Public
License and may only be used or replicated with the express permission
of Red Hat, Inc.
"""

import os.path
from tempfile import TemporaryDirectory

import requests
from bs4 import BeautifulSoup

from mdapi.confdata import standard

"""
Standard set of databases to run tests against
"""

tempargs = dict(prefix="mdapi-tests-", dir=standard.DB_FOLDER)
LOCATION = f"{TemporaryDirectory(**tempargs).name}/"

BRCHNAME = "rawhide"
PROBEURL = {
    "koji": f"https://kojipkgs.fedoraproject.org/repos/{BRCHNAME}/latest/x86_64/repodata/",
    "rawhide": f"https://dl.fedoraproject.org/pub/fedora/linux/development/{BRCHNAME}/Everything/x86_64/os/repodata/",
}
KEYWORDS = [
    "-filelists.sqlite",
    "-other.sqlite",
    "-primary.sqlite",
]
DTBSLIST = []


def databases_presence(brchname):
    """
    Return true if the databases are present of the given branch, else false
    """
    for indx in KEYWORDS:
        if not os.path.exists(f"{LOCATION}mdapi-{brchname}{indx}"):
            return False
    return True


def populate_permalinks():
    """
    Get a list of permalinks off the SQLite database archives from the specified branches
    """
    linkdict = {}
    for indx in PROBEURL.keys():
        linklist = []
        htmlcont = requests.get(PROBEURL[indx]).text  # noqa : S113
        soupobjc = BeautifulSoup(htmlcont, "html.parser")
        for jndx in soupobjc.find_all("a"):
            for kndx in KEYWORDS:
                if kndx in jndx.get("href"):
                    linklist.append(f"{PROBEURL[indx]}{jndx.get('href')}")
        linkdict[indx] = linklist
    return linkdict
