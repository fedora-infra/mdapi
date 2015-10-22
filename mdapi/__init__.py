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
import os

try:
    import simplejson as json
except ImportError:
    import json

import asyncio
from aiohttp import web

import lib as mdapilib


CONFIG = dict()
obj = __import__('default_config')
for key in dir(obj):
    if key.isupper():
        CONFIG[key] = getattr(obj, key)


if 'MDAPI_CONFIG' in os.environ and os.path.exists(os.environ['MDAPI_CONFIG']):
    with open(os.environ['MDAPI_CONFIG']) as config_file:
        exec(compile(
            config_file.read(), os.environ['MDAPI_CONFIG'], 'exec'), CONFIG)

indexfile = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'index.html')
INDEX = ''
with open(indexfile) as stream:
    INDEX = stream.read()


def _get_pkg(branch, name):
    ''' Return the pkg information for the given package in the specified
    branch or raise an aiohttp exception.
    '''
    dbfile = '%s/mdapi-%s-primary.sqlite' % (CONFIG['DB_FOLDER'], branch)
    if not os.path.exists(dbfile):
        raise web.HTTPBadRequest()

    session = mdapilib.create_session('sqlite:///%s' % dbfile)
    pkg = mdapilib.get_package(session, name)
    session.close()

    if not pkg:
        raise web.HTTPNotFound()

    return pkg


@asyncio.coroutine
def get_pkg(request):
    branch = request.match_info.get('branch')
    name = request.match_info.get('name')

    dbfile = '%s/mdapi-%s-primary.sqlite' % (CONFIG['DB_FOLDER'], branch)
    if not os.path.exists(dbfile):
        raise web.HTTPBadRequest()

    session = mdapilib.create_session('sqlite:///%s' % dbfile)
    pkg = mdapilib.get_package(session, name)

    if not pkg:
        session.close()
        raise web.HTTPNotFound()

    output = pkg.to_json()

    if pkg.rpm_sourcerpm:
        output['co-packages'] = list(set([
            cpkg.name
            for cpkg in mdapilib.get_co_packages(session, pkg.rpm_sourcerpm)
        ]))
    else:
        output['co-packages'] = []
    session.close()
    return web.Response(body=json.dumps(output).encode('utf-8'))


@asyncio.coroutine
def get_pkg_files(request):
    branch = request.match_info.get('branch')
    name = request.match_info.get('name')
    pkg = _get_pkg(branch, name)

    dbfile = '%s/mdapi-%s-filelists.sqlite' % (CONFIG['DB_FOLDER'], branch)
    if not os.path.exists(dbfile):
        raise web.HTTPBadRequest()

    session2 = mdapilib.create_session('sqlite:///%s' % dbfile)
    filelist = mdapilib.get_files(session2, pkg.pkgId)
    session2.close()
    return web.Response(body=json.dumps(
        [fileinfo.to_json() for fileinfo in filelist]).encode('utf-8'))


@asyncio.coroutine
def get_pkg_changelog(request):
    branch = request.match_info.get('branch')
    name = request.match_info.get('name')
    pkg = _get_pkg(branch, name)

    dbfile = '%s/mdapi-%s-other.sqlite' % (CONFIG['DB_FOLDER'], branch)
    if not os.path.exists(dbfile):
        raise web.HTTPBadRequest()

    session2 = mdapilib.create_session('sqlite:///%s' % dbfile)
    changelogs = mdapilib.get_changelog(session2, pkg.pkgId)
    session2.close()
    return web.Response(body=json.dumps(
        [changelog.to_json() for changelog in changelogs]).encode('utf-8'))


@asyncio.coroutine
def list_branches(request):
    ''' Return the list of all branches currently supported by mdapi
    '''
    output = list(set([
        # Remove the front part `mdapi-` and the end part -<type>.sqlite
        filename.replace('mdapi-', '').rsplit('-', 1)[0]
        for filename in os.listdir(CONFIG['DB_FOLDER'])
        if filename.startswith('mdapi') and filename.endswith('.sqlite')
    ]))
    return web.Response(body=json.dumps(output).encode('utf-8'))


@asyncio.coroutine
def index(request):
    return web.Response(body=INDEX.encode('utf-8'))


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', index)
    app.router.add_route('GET', '/branches', list_branches)
    app.router.add_route('GET', '/{branch}/pkg/{name}', get_pkg)
    app.router.add_route('GET', '/{branch}/files/{name}', get_pkg_files)
    app.router.add_route(
        'GET', '/{branch}/changelog/{name}', get_pkg_changelog)

    srv = yield from loop.create_server(
        app.make_handler(),
        CONFIG.get('HOST', '127.0.0.1'),
        CONFIG.get('PORT', 8080))
    print(
        "Server started at http://%s:%s" % (
            CONFIG.get('HOST', '127.0.0.1'),
            CONFIG.get('PORT', 8080))
    )
    return srv


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
