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

from importlib import metadata

from mdapi.confdata.standard import (  # noqa
    CRON_SLEEP,
    DB_FOLDER,
    DL_SERVER,
    DL_VERIFY,
    KOJI_REPO,
    LOGGING,
    PKGDB2_URL,
    PKGDB2_VERIFY,
    PUBLISH_CHANGES,
    repomd_xml_namespace,
)

__version__ = metadata.version("mdapi")


def compile_configuration(confobjc):
    global DB_FOLDER, LOGGING, KOJI_REPO, PKGDB2_URL, DL_SERVER, PKGDB2_VERIFY, DL_VERIFY
    global PUBLISH_CHANGES, CRON_SLEEP, repomd_xml_namespace
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
        DB_FOLDER,
        PKGDB2_URL,
        KOJI_REPO,
        DL_SERVER,
        PKGDB2_VERIFY,
        DL_VERIFY,
        PUBLISH_CHANGES,
        CRON_SLEEP,
        LOGGING,
    )
