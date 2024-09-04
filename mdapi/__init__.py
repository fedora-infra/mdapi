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

import os
import sys
from importlib import metadata
from logging import getLogger
from logging.config import dictConfig

from mdapi.confdata import servlogr, standard

__version__ = metadata.version("mdapi")


def compile_configuration(confobjc):
    standard.DB_FOLDER = confobjc.get("DB_FOLDER", standard.DB_FOLDER)
    standard.BODHI_URL = confobjc.get("BODHI_URL", standard.BODHI_URL)
    standard.KOJI_REPO = confobjc.get("KOJI_REPO", standard.KOJI_REPO)
    standard.DL_SERVER = confobjc.get("DL_SERVER", standard.DL_SERVER)
    standard.PUBLISH_CHANGES = confobjc.get("PUBLISH_CHANGES", standard.PUBLISH_CHANGES)
    standard.CRON_SLEEP = confobjc.get("CRON_SLEEP", standard.CRON_SLEEP)
    standard.LOGGING = confobjc.get("LOGGING", standard.LOGGING)
    standard.repomd_xml_namespace = confobjc.get(
        "repomd_xml_namespace", standard.repomd_xml_namespace
    )
    standard.APPSERVE = confobjc.get("APPSERVE", standard.APPSERVE)

    if not os.path.exists(standard.DB_FOLDER):
        # Cannot pull/push data from/into directory that does not exist
        print("Database directory not found")
        sys.exit(1)

    dictConfig(standard.LOGGING)
    servlogr.logrobjc = getLogger(__name__)
