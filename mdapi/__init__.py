# -*- coding: utf-8 -*-
#
# Copyright © 2015  Red Hat, Inc.
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
Top level of the mdapi Flask application.
'''

import json

import asyncio
from aiohttp import web

import lib as mdapilib

@asyncio.coroutine
def get_pkg(request):
    name = request.match_info.get('name', None)
    session = mdapilib.create_session('sqlite:////var/tmp/rawhide-primary.sqlite')
    pkg = mdapilib.get_package(session, name)
    session.close()
    if not pkg:
        raise web.HTTPNotFound()
    return web.Response(body=json.dumps(pkg.to_json()).encode('utf-8'))


@asyncio.coroutine
def get_pkg_files(request):
    name = request.match_info.get('name', None)
    session = mdapilib.create_session(
        'sqlite:////var/tmp/20151022-rawhide-primary.sqlite')
    pkg = mdapilib.get_package(session, name)
    session.close()
    if not pkg:
        raise web.HTTPNotFound()

    session2 = mdapilib.create_session(
        'sqlite:////var/tmp/20151022-rawhide-filelists.sqlite')
    filelist = mdapilib.get_files(session2, pkg.pkgId)
    session2.close()
    return web.Response(body=json.dumps(
        [fileinfo.to_json() for fileinfo in filelist]).encode('utf-8'))


@asyncio.coroutine
def get_pkg_changelog(request):
    name = request.match_info.get('name', None)
    session = mdapilib.create_session(
        'sqlite:////var/tmp/20151022-rawhide-primary.sqlite')
    pkg = mdapilib.get_package(session, name)
    session.close()
    if not pkg:
        raise web.HTTPNotFound()

    session2 = mdapilib.create_session(
        'sqlite:////var/tmp/20151022-rawhide-other.sqlite')
    changelogs = mdapilib.get_changelog(session2, pkg.pkgId)
    session2.close()
    return web.Response(body=json.dumps(
        [changelog.to_json() for changelog in changelogs]).encode('utf-8'))


@asyncio.coroutine
def index(request):
    text = "Front page"
    return web.Response(body=text.encode('utf-8'))


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    app.router.add_route('GET', '/pkg/{name}', get_pkg)
    app.router.add_route('GET', '/files/{name}', get_pkg_files)
    app.router.add_route('GET', '/changelog/{name}', get_pkg_changelog)

    srv = yield from loop.create_server(
        app.make_handler(), '127.0.0.1', 8080)
    print("Server started at http://127.0.0.1:8080")
    return srv


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass
