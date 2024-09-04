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
from pathlib import PurePath

import pytest
from requests.exceptions import HTTPError

import tests
from mdapi.confdata import servlogr
from mdapi.database import main
from mdapi.database.main import extract_database, fetch_database


@pytest.fixture
def setup_environment():
    """
    Collect the SQLite databases from the mirror
    to have some data to test against
    """
    if tests.databases_presence("rawhide") and tests.databases_presence("koji"):
        pass
    else:
        if not os.path.exists(tests.LOCATION):
            os.mkdir(tests.LOCATION)
        linkdict = tests.populate_permalinks()
        for indx in linkdict.keys():
            for filelink in linkdict[indx]:
                arcvloca = f"{tests.LOCATION}{PurePath(filelink).name}"
                fileloca = f"{tests.LOCATION}{PurePath(filelink).name.replace(PurePath(filelink).name.split('-')[0], f'mdapi-{indx}')}"  # noqa: E501
                fileloca = fileloca.replace(f".{fileloca.split('.')[-1]}", "")
                try:
                    fetch_database(indx, filelink, arcvloca)
                    extract_database(indx, arcvloca, fileloca)
                    os.remove(arcvloca)
                except HTTPError as excp:
                    servlogr.logrobjc.warning(f"[{indx}] Archive could not be fetched : {excp}")


@pytest.mark.download_required
def test_fetch_and_extract_database(setup_environment):
    for indx in tests.PROBEURL.keys():
        assert tests.databases_presence(indx)  # noqa : S101
    assert len(os.listdir(tests.LOCATION)) == 6  # noqa : S101


@pytest.mark.download_required
@pytest.mark.parametrize(
    "dvlpstat",
    [
        "current",
        "pending",
        "frozen",
    ],
)
def test_list_branches(dvlpstat):
    rsltobjc = main.list_branches(dvlpstat)
    assert isinstance(rsltobjc, list)  # noqa : S101
    assert len(rsltobjc) > 0  # noqa : S101
