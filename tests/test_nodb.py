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


import pytest

from mdapi.confdata import standard
from mdapi.services.main import buildapp


@pytest.fixture
async def testing_application_nodb(event_loop, aiohttp_client):
    standard.DB_FOLDER = "."
    applobjc = await buildapp()
    return await aiohttp_client(applobjc)


async def test_view_index_page(testing_application_nodb):
    respobjc = await testing_application_nodb.get("/")
    assert respobjc.status == 200
    botmtext = "2015-2022 - Red Hat, Inc. - GPLv3+ - Sources:"
    otptrslt = await respobjc.text()
    assert botmtext in otptrslt


async def test_view_branches(testing_application_nodb):
    respobjc = await testing_application_nodb.get("/branches")
    assert respobjc.status == 200
    assert "[]" == await respobjc.text()


async def test_view_pkg_rawhide(testing_application_nodb):
    respobjc = await testing_application_nodb.get("/rawhide/pkg/kernel")
    assert respobjc.status == 400
    assert "400: Bad Request" == await respobjc.text()


async def test_view_pkg_rawhide_invalid(testing_application_nodb):
    respobjc = await testing_application_nodb.get("/rawhide/pkg/invalidpackagename")
    assert respobjc.status == 400
    assert "400: Bad Request" == await respobjc.text()


async def test_view_srcpkg_rawhide(testing_application_nodb):
    respobjc = await testing_application_nodb.get("/rawhide/srcpkg/python-natsort")
    assert respobjc.status == 400
    assert "400: Bad Request" == await respobjc.text()


async def test_view_filelist_rawhide(testing_application_nodb):
    respobjc = await testing_application_nodb.get("/rawhide/files/kernel-core")
    assert respobjc.status == 400
    assert "400: Bad Request" == await respobjc.text()


async def test_view_changelog_rawhide(testing_application_nodb):
    respobjc = await testing_application_nodb.get("/rawhide/changelog/kernel")
    assert respobjc.status == 400
    assert "400: Bad Request" == await respobjc.text()


@pytest.mark.parametrize(
    "action",
    [
        "requires",
        "provides",
        "obsoletes",
        "conflicts",
        "enhances",
        "recommends",
        "suggests",
        "supplements",
    ],
)
async def test_view_property_koji(testing_application_nodb, action):
    respobjc = await testing_application_nodb.get("/koji/%s/R" % (action))
    assert respobjc.status == 400
    assert "400: Bad Request" == await respobjc.text()
