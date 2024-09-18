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

import pytest
from click.testing import CliRunner

from mdapi import __version__
from mdapi.main import main


@pytest.mark.download_needless
def test_cli_application_help_option():
    rnnrobjc = CliRunner()
    rsltobjc = rnnrobjc.invoke(main, ["--help"])
    assert "A simple API for serving the metadata from the RPM repositories" in rsltobjc.output  # noqa : S101
    assert rsltobjc.exit_code == 0  # noqa : S101


@pytest.mark.download_needless
def test_cli_application_version_option():
    rnnrobjc = CliRunner()
    rsltobjc = rnnrobjc.invoke(main, ["--version"])
    assert rsltobjc.output == f"mdapi, version {__version__}\n"  # noqa : S101
    assert rsltobjc.exit_code == 0  # noqa : S101


@pytest.mark.download_needless
def test_cli_application_with_wrong_configpath_and_no_command():
    rnnrobjc = CliRunner()
    confpath = "/etc/mdapi/myconfig.py"
    rsltobjc = rnnrobjc.invoke(main, ["--conffile", confpath])
    assert f"Error: Invalid value for '-c' / '--conffile': Path '{confpath}' does not exist." in rsltobjc.output  # noqa : S101
    assert rsltobjc.exit_code == 2  # noqa : S101


@pytest.mark.download_needless
def test_cli_application_with_right_configpath_but_no_command():
    rnnrobjc = CliRunner()
    confpath = os.path.dirname(__file__).replace("tests", "mdapi/confdata/standard.py")
    rsltobjc = rnnrobjc.invoke(main, ["--conffile", confpath])
    assert "Error: Missing command." in rsltobjc.output  # noqa : S101
    assert rsltobjc.exit_code == 2  # noqa : S101
