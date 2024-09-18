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

"""
mdapi default configuration.
"""

# url to the database server:
DB_FOLDER = "/var/tmp"  # noqa : S108

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(message)s",
            "datefmt": "[%Y-%m-%d %I:%M:%S %z]",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    # The root logger configuration; this is a catch-all configuration
    # that applies to all log messages not handled by a different logger
    "root": {
        "level": "INFO",
        "handlers": ["console"],
    },
}

"""
Database fetching configuration
"""

KOJI_REPO = "https://kojipkgs.fedoraproject.org/repos"
BODHI_URL = "https://bodhi.fedoraproject.org"
DL_SERVER = "https://dl.fedoraproject.org"

# Whether to publish to Fedora Messaging
PUBLISH_CHANGES = False

# How long to wait between retries if processing failed
CRON_SLEEP = 30

repomd_xml_namespace = {
    "repo": "http://linux.duke.edu/metadata/repo",
    "rpm": "http://linux.duke.edu/metadata/rpm",
}

"""
Application service configuration
"""

APPSERVE = {
    "logging": {"level": LOGGING["root"]["level"]},
    "bind": "0.0.0.0:8080",
    "worker_class": "aiohttp.GunicornUVLoopWebWorker",
}
