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
from requests.exceptions import HTTPError

from mdapi.confdata.servlogr import logrobjc
from mdapi.database.main import extract_database, fetch_database

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


def populate_test_databases():
    """
    Create a directory for populating the test database directory
    (That is if it does not exist)
    """

    if not databases_presence("rawhide") or not databases_presence("koji"):
        if not os.path.exists("/var/tmp/mdapi-tests/"):
            os.mkdir("/var/tmp/mdapi-tests/")

        """
        Create a list of links, download and extract them from the specified source
        """
        for kndx in PROBEURL.keys():
            htmlcont = requests.get(PROBEURL[kndx]).text
            soupobjc = BeautifulSoup(htmlcont, "html.parser")
            for indx in soupobjc.find_all("a"):
                for jndx in KEYWORDS:
                    if jndx in indx.get("href"):
                        dtbslink = "%s%s" % (PROBEURL[kndx], indx.get("href"))
                        arcvloca = "%s%s" % (LOCATION, indx.get("href"))
                        fileloca = "%s%s" % (
                            LOCATION,
                            indx.get("href").replace(
                                indx.get("href").split("-")[0], "mdapi-%s" % kndx
                            ),
                        )
                        fileloca = fileloca.replace(".%s" % indx.get("href").split(".")[-1], "")
                        try:
                            fetch_database(kndx, dtbslink, arcvloca)
                            extract_database(kndx, arcvloca, fileloca)
                            os.remove(arcvloca)
                        except HTTPError as excp:
                            logrobjc.warning("[%s] Archive could not be found : %s" % (kndx, excp))
