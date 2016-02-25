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
Top level of the mdapi aiohttp application.
'''
import json
import os
import urllib


import asyncio
import werkzeug
from aiohttp import web, MultiDict

import mdapi.lib as mdapilib
import mdapi.file_lock as file_lock


CONFIG = dict()
obj = werkzeug.import_string('mdapi.default_config')
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
    INDEX = INDEX.replace('$PREFIX', CONFIG.get('PREFIX', ''))


def _get_pkg(branch, name, action=None):
    ''' Return the pkg information for the given package in the specified
    branch or raise an aiohttp exception.
    '''
    pkg = None
    wrongdb = False
    for repotype in ['updates-testing', 'updates', 'testing', None]:

        if repotype:
            dbfile = '%s/mdapi-%s-%s-primary.sqlite' % (
                CONFIG['DB_FOLDER'], branch, repotype)
        else:
            dbfile = '%s/mdapi-%s-primary.sqlite' % (CONFIG['DB_FOLDER'], branch)

        if not os.path.exists(dbfile):
            wrongdb = True
            continue

        wrongdb = False

        with file_lock.FileFlock(dbfile + '.lock'):
            session = mdapilib.create_session('sqlite:///%s' % dbfile)
            if action:
                pkg = mdapilib.get_package_by(session, action, name)
            else:
                pkg = mdapilib.get_package(session, name)
            session.close()
        if pkg:
            break

    if wrongdb:
        raise web.HTTPBadRequest()

    if not pkg:
        raise web.HTTPNotFound()

    return (pkg, repotype)


def _get_pretty(request):
    pretty = False
    get_params = MultiDict(urllib.parse.parse_qsl(request.query_string.lower()))
    if get_params.get('pretty'):
        if str(get_params.get('pretty', None)) in ['1', 'true']:
            pretty = True
    # Assume pretty if html is requested and pretty is not disabled
    elif 'text/html' in request.headers.get('ACCEPT', ''):
        pretty = True
    return pretty


def _expand_pkg_info(pkgs, branch, repotype=None):
    ''' Return a JSON blob containing all the information we want to return
    for the provided package or packages.
    '''
    singleton = False
    if not isinstance(pkgs, (list, tuple)):
        singleton = True
        pkgs = [pkgs]
    output = []
    for pkg in pkgs:
        out = pkg.to_json()
        dbfile = '%s/mdapi-%s%s-primary.sqlite' % (
            CONFIG['DB_FOLDER'], branch, '-%s' % repotype if repotype else '')

        with file_lock.FileFlock(dbfile + '.lock'):
            session = mdapilib.create_session('sqlite:///%s' % dbfile)
            # Fill in some extra info

            # Basic infos, always present regardless of the version of the repo
            for datatype in ['conflicts', 'obsoletes', 'provides', 'requires']:
                data = mdapilib.get_package_info(
                    session, pkg.pkgKey, datatype.capitalize())
                if data:
                    out[datatype] = [item.to_json() for item in data]
                else:
                    out[datatype] = data

            # New meta-data present for soft dependency management in RPM
            for datatype in ['enhances', 'recommends', 'suggests', 'supplements']:
                data = mdapilib.get_package_info(
                    session, pkg.pkgKey, datatype.capitalize())
                if data:
                    out[datatype] = [item.to_json() for item in data]
                else:
                    out[datatype] = data

            # Add the list of packages built from the same src.rpm
            if pkg.rpm_sourcerpm:
                out['co-packages'] = list(set([
                    cpkg.name
                    for cpkg in mdapilib.get_co_packages(session, pkg.rpm_sourcerpm)
                ]))
            else:
                out['co-packages'] = []
            out['repo'] = repotype if repotype else 'release'
            session.close()
        output.append(out)
    if singleton:
        return output[0]
    else:
        return output


@asyncio.coroutine
def get_pkg(request):
    branch = request.match_info.get('branch')
    pretty = _get_pretty(request)
    name = request.match_info.get('name')
    pkg, repotype = _get_pkg(branch, name)

    output = _expand_pkg_info(pkg, branch, repotype)

    args = {}
    if pretty:
        args = dict(sort_keys=True, indent=4, separators=(',', ': '))

    return web.Response(body=json.dumps(output, **args).encode('utf-8'))


@asyncio.coroutine
def get_pkg_files(request):
    branch = request.match_info.get('branch')
    name = request.match_info.get('name')
    pretty = _get_pretty(request)
    pkg, repotype = _get_pkg(branch, name)

    dbfile = '%s/mdapi-%s%s-filelists.sqlite' % (
        CONFIG['DB_FOLDER'], branch, '-%s' % repotype if repotype else '')
    if not os.path.exists(dbfile):
        raise web.HTTPBadRequest()

    with file_lock.FileFlock(dbfile + '.lock'):
        session2 = mdapilib.create_session('sqlite:///%s' % dbfile)
        filelist = mdapilib.get_files(session2, pkg.pkgId)
        session2.close()

    output = {
        'files': [fileinfo.to_json() for fileinfo in filelist],
        'repo': repotype if repotype else 'release',
    }
    args = {}
    if pretty:
        args = dict(sort_keys=True, indent=4, separators=(',', ': '))

    return web.Response(body=json.dumps(output, **args).encode('utf-8'))


@asyncio.coroutine
def get_pkg_changelog(request):
    branch = request.match_info.get('branch')
    name = request.match_info.get('name')
    pretty = _get_pretty(request)
    pkg, repotype = _get_pkg(branch, name)

    dbfile = '%s/mdapi-%s%s-other.sqlite' % (
        CONFIG['DB_FOLDER'], branch, '-%s' % repotype if repotype else '')
    if not os.path.exists(dbfile):
        raise web.HTTPBadRequest()

    with file_lock.FileFlock(dbfile + '.lock'):
        session2 = mdapilib.create_session('sqlite:///%s' % dbfile)
        changelogs = mdapilib.get_changelog(session2, pkg.pkgId)
        session2.close()

    output = {
        'changelogs': [changelog.to_json() for changelog in changelogs],
        'repo': repotype if repotype else 'release',
    }
    args = {}
    if pretty:
        args = dict(sort_keys=True, indent=4, separators=(',', ': '))

    return web.Response(body=json.dumps(output, **args).encode('utf-8'))


@asyncio.coroutine
def list_branches(request):
    ''' Return the list of all branches currently supported by mdapi
    '''
    pretty = _get_pretty(request)
    output = list(set([
        # Remove the front part `mdapi-` and the end part -<type>.sqlite
        filename.replace('mdapi-', '').rsplit('-', 2)[0].replace('-updates', '')
        for filename in os.listdir(CONFIG['DB_FOLDER'])
        if filename.startswith('mdapi') and filename.endswith('.sqlite')
    ]))

    args = {}
    if pretty:
        args = dict(sort_keys=True, indent=4, separators=(',', ': '))

    return web.Response(body=json.dumps(output, **args).encode('utf-8'))


def process_dep(request, action):
    ''' Return the information about the packages having the specified
    action (provides, requires, obsoletes...)
    '''
    branch = request.match_info.get('branch')
    pretty = _get_pretty(request)
    name = request.match_info.get('name')

    pkg, repotype = _get_pkg(branch, name, action=action)

    output = _expand_pkg_info(pkg, branch, repotype)

    args = {}
    if pretty:
        args = dict(sort_keys=True, indent=4, separators=(',', ': '))

    return web.Response(body=json.dumps(output, **args).encode('utf-8'))


@asyncio.coroutine
def get_provides(request):
    return process_dep(request, 'provides')


@asyncio.coroutine
def get_requires(request):
    return process_dep(request, 'requires')


@asyncio.coroutine
def get_obsoletes(request):
    return process_dep(request, 'obsoletes')


@asyncio.coroutine
def index(request):
    return web.Response(body=INDEX.encode('utf-8'))


@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop)
    routes = []
    prefix = CONFIG.get('PREFIX', '')
    if prefix:
        routes.append(('', index))

    routes.extend([
        ('/', index),
        ('/branches', list_branches),
        ('/{branch}/pkg/{name}', get_pkg),
        ('/{branch}/provides/{name}', get_provides),
        ('/{branch}/requires/{name}', get_requires),
        ('/{branch}/obsoletes/{name}', get_obsoletes),
        ('/{branch}/files/{name}', get_pkg_files),
        ('/{branch}/changelog/{name}', get_pkg_changelog),
    ])
    for route in routes:
        app.router.add_route('GET', prefix + route[0], route[1])

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
