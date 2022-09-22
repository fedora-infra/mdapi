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

import pytest

from mdapi.database import main
from tests import LOCATION, PROBEURL, databases_presence, populate_test_databases


@pytest.mark.parametrize(
    "dvlpstat",
    [
        "Active",
        "Under Development",
    ],
)
def test_list_branches(dvlpstat):
    rsltobjc = main.list_branches(dvlpstat)
    assert isinstance(rsltobjc, list)
    assert len(rsltobjc) > 0


def test_fetch_and_extract_database():
    populate_test_databases()
    for indx in PROBEURL.keys():
        assert databases_presence(indx)
    assert len(os.listdir(LOCATION)) == 6
