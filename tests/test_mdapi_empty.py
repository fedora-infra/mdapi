#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# Copyright © 2019  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions
# of the GNU General Public License v.2, or (at your option) any later
# version.  This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY expressed or implied, including the
# implied warranties of MERCHANTABILITY or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.  You
# should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# Any Red Hat trademarks that are incorporated in the source
# code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission
# of Red Hat, Inc.
#

'''
Tests for mdapi.

'''
import os
import shutil
import subprocess
import sys
import tempfile

import pytest
from aiohttp import web

sys.path.insert(0, os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..'))

import mdapi

HERE = os.path.join(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture
def cli(loop, aiohttp_client):
    mdapi.CONFIG['DB_FOLDER'] = '.'
    app = web.Application()
    app = mdapi._set_routes(app)
    return loop.run_until_complete(aiohttp_client(app))


async def test_view_index_page(cli):
    resp = await cli.get('/')
    assert resp.status == 200
    header = r"""
               _             _
              | |           (_)
 _ __ ___   __| | __ _ _ __  _
| '_ ` _ \ / _` |/ _` | '_ \| |
| | | | | | (_| | (_| | |_) | |
|_| |_| |_|\__,_|\__,_| .__/|_|
                      | |
                      |_|
"""
    output = await resp.text()
    assert header in output


async def test_view_branches(cli):
    resp = await cli.get('/branches')
    assert resp.status == 200
    assert '[]' == await resp.text()


async def test_view_pkg_rawhide(cli):
    resp = await cli.get('/rawhide/pkg/kernel')
    assert resp.status == 400
    assert '400: Bad Request' == await resp.text()


async def test_view_pkg_rawhide_invalid(cli):
    resp = await cli.get('/rawhide/pkg/invalidpackagename')
    assert resp.status == 400
    assert '400: Bad Request' == await resp.text()


async def test_view_srcpkg_rawhide(cli):
    resp = await cli.get('/rawhide/srcpkg/python-natsort')
    assert resp.status == 400
    assert '400: Bad Request' == await resp.text()


async def test_view_file_list_rawhide(cli):
    resp = await cli.get('/rawhide/files/kernel-core')
    assert resp.status == 400
    assert '400: Bad Request' == await resp.text()


async def test_view_changelog_rawhide(cli):
    resp = await cli.get('/rawhide/changelog/kernel')
    assert resp.status == 400
    assert '400: Bad Request' == await resp.text()


@pytest.mark.parametrize("action", [
    "requires", "provides", "obsoletes", "conflicts",
    "enhances", "recommends", "suggests", "supplements",
])
async def test_view_property_koji(cli, action):
    resp = await cli.get('/koji/%s/R' % action)
    assert resp.status == 400
    assert '400: Bad Request' == await resp.text()
