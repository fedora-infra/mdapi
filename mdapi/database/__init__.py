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

import time

from mdapi.confdata.standard import DB_FOLDER, LOGGING, KOJI_REPO, PKGDB2_URL, DL_SERVER, PKGDB2_VERIFY, DL_VERIFY, PUBLISH_CHANGES, CRON_SLEEP, repomd_xml_namespace
from mdapi.database.main import list_branches, process_repo
from mdapi.confdata.servlogr import logrobjc


def index_repositories():
    repolist = []

    # Obtain the development repos (rawhide + eventually Fn+1 branched)
    dev_releases = list_branches(status="Under Development")
    for rels in dev_releases:
        if rels["status"] != "Under Development":
            continue
        versdata = rels["version"]
        if versdata == "devel":
            versdata = "rawhide"
        urlx = "%s/pub/fedora/linux/development/%s/Everything/x86_64/os/repodata" % (DL_SERVER, versdata)
        logrobjc.info("Acquired repo for %s/%s of '%s' branch at %s" % (rels["koji_name"], versdata, rels["status"], urlx))
        repolist.append(
            (urlx, rels["koji_name"])
        )
        urlx = urlx.replace("/x86_64/os/", "/source/tree/")
        repolist.append((urlx, "src_%s" % rels["koji_name"]))

    urls = {
        "Fedora Linux":
            [
                "%s/pub/fedora/linux/releases/%s/Everything/x86_64/os/repodata",
                "%s/pub/fedora/linux/updates/%s/Everything/x86_64/repodata",
                "%s/pub/fedora/linux/updates/testing/%s/Everything/x86_64/repodata",
            ],
        "Fedora EPEL":
            [
                "%s/pub/epel/%s/x86_64/repodata/",
                "%s/pub/epel/testing/%s/x86_64/repodata",
            ]
    }

    urls["Fedora"] = urls["Fedora Linux"]
    repodict = {
        "fedora": ["%s", "%s-updates", "%s-updates-testing"],
        "epel": ["%s", "%s-testing"]
    }

    # Obtain the stable repos
    stable_releases = list_branches(status="Active")
    for rels in stable_releases:
        if rels["status"] != "Active":
            continue
        versdata = rels["version"]
        for jndx, urli in enumerate(urls[rels["name"]]):
            if rels["name"] in ("Fedora Linux", "Fedora"):
                name = repodict["fedora"][jndx] % rels["koji_name"]
            elif rels["name"] == "Fedora EPEL" and versdata == "8":
                name = repodict["epel"][jndx] % rels["koji_name"]
                urli = urli.replace("/x86_64/", "/Everything/x86_64/")
            else:
                name = repodict["epel"][jndx] % rels["koji_name"]
            rurl = urli % (DL_SERVER, versdata)
            repolist.append((rurl, name))
            rurl = rurl.replace("/x86_64/os", "/source/tree")
            repolist.append((rurl, "src_%s" % name))

    # Finish with the koji repo
    repolist.append(
        ("%s/rawhide/latest/x86_64/repodata" % KOJI_REPO, "koji")
    )

    # In serial
    for repo in repolist:
        loop = True
        qant = 0
        while loop:
            qant += 1
            try:
                process_repo(repo)
                loop = False
            except OSError:
                if qant == 4:
                    raise
                # Most often due to an invalid stream, so let us try again
                time.sleep(CRON_SLEEP)
                process_repo(repo)


def compile_configuration(confobjc):
    global DB_FOLDER, LOGGING, KOJI_REPO, PKGDB2_URL, DL_SERVER, PKGDB2_VERIFY, DL_VERIFY, PUBLISH_CHANGES, CRON_SLEEP, repomd_xml_namespace
    DB_FOLDER = confobjc.get("DB_FOLDER", DB_FOLDER)
    PKGDB2_URL = confobjc.get("PKGDB2_URL", PKGDB2_URL)
    KOJI_REPO = confobjc.get("KOJI_REPO", KOJI_REPO)
    DL_SERVER = confobjc.get("DL_SERVER", DL_SERVER)
    PKGDB2_VERIFY = confobjc.get("PKGDB2_VERIFY", PKGDB2_VERIFY)
    DL_VERIFY = confobjc.get("DL_VERIFY", DL_VERIFY)
    PUBLISH_CHANGES = confobjc.get("PUBLISH_CHANGES", PUBLISH_CHANGES)
    CRON_SLEEP = confobjc.get("CRON_SLEEP", CRON_SLEEP)
    LOGGING = confobjc.get("LOGGING", LOGGING)
    return (
        DB_FOLDER, PKGDB2_URL, KOJI_REPO, DL_SERVER, PKGDB2_VERIFY, DL_VERIFY, PUBLISH_CHANGES, CRON_SLEEP, LOGGING
    )
