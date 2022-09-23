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

import requests
from bs4 import BeautifulSoup

"""
Standard set of databases to run tests against
"""

LOCATION = "/var/tmp/mdapi-tests/"
BRCHNAME = "rawhide"
PROBEURL = {
    "koji": "https://kojipkgs.fedoraproject.org/repos/%s/latest/x86_64/repodata/" % BRCHNAME,
    "rawhide": "https://dl.fedoraproject.org/pub/fedora/linux/development/%s/Everything/x86_64/os/repodata/"  # noqa
    % BRCHNAME,
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
        if not os.path.exists("%smdapi-%s%s" % (LOCATION, brchname, indx)):
            return False
    return True


def populate_permalinks():
    """
    Get a list of permalinks oft the SQLite database archives from the specified branches
    """
    linkdict = {}
    for indx in PROBEURL.keys():
        linklist = []
        htmlcont = requests.get(PROBEURL[indx]).text
        soupobjc = BeautifulSoup(htmlcont, "html.parser")
        for jndx in soupobjc.find_all("a"):
            for kndx in KEYWORDS:
                if kndx in jndx.get("href"):
                    linklist.append("%s%s" % (PROBEURL[indx], jndx.get("href")))
        linkdict[indx] = linklist
    return linkdict
