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

import logging
import logging.config
import os

import click
import requests
from aiohttp.web import run_app  # noqa

from mdapi import __version__, compile_configuration
from mdapi.confdata.servlogr import logrobjc  # noqa
from mdapi.database.main import index_repositories
from mdapi.services.main import buildapp  # noqa


@click.group(name="mdapi")
@click.option(
    "-c",
    "--conffile",
    "conffile",
    type=click.Path(exists=True),
    help="Read configuration from the specified Python file",
    default=None,
)
@click.version_option(version=__version__, prog_name="mdapi")
def main(conffile=None):
    """
    A simple API for serving the metadata from the RPM repositories
    """
    if conffile is not None:
        # Load the configuration file to use
        CONFIG = {}
        with open(conffile, "r") as confobjc:
            exec(compile(confobjc.read(), conffile, "exec"), CONFIG)
        (
            DB_FOLDER,
            PKGDB2_URL,
            KOJI_REPO,
            DL_SERVER,
            PKGDB2_VERIFY,
            DL_VERIFY,
            PUBLISH_CHANGES,
            CRON_SLEEP,
            LOGGING,
        ) = compile_configuration(CONFIG)

        if not os.path.exists(DB_FOLDER):
            # Cannot pull/push data from/into directory that does not exist
            print("Database directory not found")
            return 1

        if not DL_VERIFY or not PKGDB2_VERIFY:
            # Suppress urllib3's warnings about insecure requests
            requests.packages.urllib3.disable_warnings()

        logging.config.dictConfig(LOGGING)
        global logrobjc
        logrobjc = logging.getLogger(__name__)
    print(logrobjc.getEffectiveLevel())


@main.command(
    name="database", help="Fetch SQLite databases from all active Fedora Linux and EPEL branches"
)
def database():
    index_repositories()


@main.command(name="serveapp", help="Start the API server for querying repository metadata")
def serveapp():
    print("Hello world!")


if __name__ == "__main__":
    main()
