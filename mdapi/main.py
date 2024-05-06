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

import subprocess

import click

from mdapi import __version__, compile_configuration
from mdapi.confdata.standard import APPSERVE
from mdapi.database.main import index_repositories


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
        with open(conffile) as confobjc:
            exec(compile(confobjc.read(), conffile, "exec"), CONFIG)  # noqa : S102
        compile_configuration(CONFIG)


@main.command(
    name="database", help="Fetch SQLite databases from all active Fedora Linux and EPEL branches"
)
def database():
    index_repositories()


@main.command(name="serveapp", help="Start the API server for querying repository metadata")
def serveapp():
    try:
        startcmd = (
            f"gunicorn mdapi.services.main:buildapp --bind {APPSERVE['bind']} --worker-class {APPSERVE['worker_class']} --log-level {APPSERVE['logging']['level']}"  # noqa
        )
        subprocess.run(startcmd.split())  # noqa : S603
    except KeyError:
        print("Invalid configuration detected")
        return 1


if __name__ == "__main__":
    main()
