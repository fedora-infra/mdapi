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
import functools
import json
import logging
import logging.config
import os
import urllib
from urllib.parse import parse_qs

import asyncio
import werkzeug
from aiohttp import web
from multidict import MultiDict
from flufl.lock import Lock

import mdapi.lib as mdapilib



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


_log = logging.getLogger(__name__)


def allows_jsonp(function):
    ''' Add support for JSONP queries to the endpoint decorated. '''

    @functools.wraps(function)
    def wrapper(request, *args, **kwargs):
        ''' Actually does the job with the arguments provided.

        :arg request: the request that was called that we want to add JSONP
        support to
        :type request: aiohttp.web_request.Request

        '''
        response = yield from function(request, *args, **kwargs)
        url_arg = parse_qs(request.query_string)
        callback = url_arg.get('callback')
        if callback and request.method == 'GET':
            if isinstance(callback, list):
                callback = callback[0]
            response.mimetype = 'application/javascript'
            response.content_type = 'application/javascript'
            response.text = '%s(%s);' % (callback, response.text)

        return response

    return wrapper


@asyncio.coroutine
def _get_pkg(branch, name=None, action=None, srcname=None):
    ''' Return the pkg information for the given package in the specified
    branch or raise an aiohttp exception.
    '''
    if (not name and not srcname) or (name and srcname):
        raise web.HTTPBadRequest()

    pkg = None
    wrongdb = False
    for repotype in ['updates-testing', 'updates', 'testing', None]:

        if repotype:
            dbfile = '%s/mdapi-%s-%s-primary.sqlite' % (
                CONFIG['DB_FOLDER'], branch, repotype)
        else:
            dbfile = '%s/mdapi-%s-primary.sqlite' % (
                CONFIG['DB_FOLDER'], branch)

        if not os.path.exists(dbfile):
            wrongdb = True
            continue

        wrongdb = False

        with Lock(dbfile + '.lock'):
            session = yield from mdapilib.create_session(
                'sqlite:///%s' % dbfile)
            if name:
                if action:
                    pkg = yield from mdapilib.get_package_by(
                        session, action, name)
                else:
                    pkg = yield from mdapilib.get_package(session, name)
            elif srcname:
                pkg = yield from mdapilib.get_package_by_src(session, srcname)
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
    get_params = MultiDict(urllib.parse.parse_qsl(
        request.query_string.lower()))
    if get_params.get('pretty'):
        if str(get_params.get('pretty', None)) in ['1', 'true']:
            pretty = True
    # Assume pretty if html is requested and pretty is not disabled
    elif 'text/html' in request.headers.get('ACCEPT', ''):
        pretty = True
    return pretty


@asyncio.coroutine
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

        with Lock(dbfile + '.lock'):
            session = yield from mdapilib.create_session(
                'sqlite:///%s' % dbfile)
            # Fill in some extra info

            # Basic infos, always present regardless of the version of the repo
            for datatype in ['conflicts', 'obsoletes', 'provides', 'requires']:
                data = yield from mdapilib.get_package_info(
                    session, pkg.pkgKey, datatype.capitalize())
                if data:
                    out[datatype] = [item.to_json() for item in data]
                else:
                    out[datatype] = data

            # New meta-data present for soft dependency management in RPM
            for datatype in [
                    'enhances', 'recommends', 'suggests', 'supplements']:
                data = yield from mdapilib.get_package_info(
                    session, pkg.pkgKey, datatype.capitalize())
                if data:
                    out[datatype] = [item.to_json() for item in data]
                else:
                    out[datatype] = data

            # Add the list of packages built from the same src.rpm
            if pkg.rpm_sourcerpm:
                copkgs = yield from mdapilib.get_co_packages(
                    session, pkg.rpm_sourcerpm)
                out['co-packages'] = list(set([
                    cpkg.name for cpkg in copkgs
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
@allows_jsonp
def get_pkg(request):
    _log.info('get_pkg %s', request)
    branch = request.match_info.get('branch')
    pretty = _get_pretty(request)
    name = request.match_info.get('name')
    pkg, repotype = yield from _get_pkg(branch, name)

    output = yield from _expand_pkg_info(pkg, branch, repotype)

    args = {}
    if pretty:
        args = dict(sort_keys=True, indent=4, separators=(',', ': '))

    output = web.Response(
        body=json.dumps(output, **args).encode('utf-8'),
        content_type='application/json')
    return output


@asyncio.coroutine
@allows_jsonp
def get_src_pkg(request):
    _log.info('get_src_pkg %s', request)
    branch = request.match_info.get('branch')
    pretty = _get_pretty(request)
    name = request.match_info.get('name')
    pkg, repotype = yield from _get_pkg(branch, srcname=name)

    output = yield from _expand_pkg_info(pkg, branch, repotype)

    args = {}
    if pretty:
        args = dict(sort_keys=True, indent=4, separators=(',', ': '))

    return web.Response(
        body=json.dumps(output, **args).encode('utf-8'),
        content_type='application/json')


@asyncio.coroutine
@allows_jsonp
def get_pkg_files(request):
    _log.info('get_pkg_files %s', request)
    branch = request.match_info.get('branch')
    name = request.match_info.get('name')
    pretty = _get_pretty(request)
    pkg, repotype = yield from _get_pkg(branch, name)

    dbfile = '%s/mdapi-%s%s-filelists.sqlite' % (
        CONFIG['DB_FOLDER'], branch, '-%s' % repotype if repotype else '')
    if not os.path.exists(dbfile):
        raise web.HTTPBadRequest()

    with Lock(dbfile + '.lock'):
        session2 = yield from mdapilib.create_session(
            'sqlite:///%s' % dbfile)
        filelist = yield from mdapilib.get_files(session2, pkg.pkgId)
        session2.close()

    output = {
        'files': [fileinfo.to_json() for fileinfo in filelist],
        'repo': repotype if repotype else 'release',
    }
    args = {}
    if pretty:
        args = dict(sort_keys=True, indent=4, separators=(',', ': '))

    return web.Response(
        body=json.dumps(output, **args).encode('utf-8'),
        content_type='application/json')


@asyncio.coroutine
@allows_jsonp
def get_pkg_changelog(request):
    _log.info('get_pkg_changelog %s', request)
    branch = request.match_info.get('branch')
    name = request.match_info.get('name')
    pretty = _get_pretty(request)
    pkg, repotype = yield from _get_pkg(branch, name)

    dbfile = '%s/mdapi-%s%s-other.sqlite' % (
        CONFIG['DB_FOLDER'], branch, '-%s' % repotype if repotype else '')
    if not os.path.exists(dbfile):
        raise web.HTTPBadRequest()

    with Lock(dbfile + '.lock'):
        session2 = yield from mdapilib.create_session(
            'sqlite:///%s' % dbfile)
        changelogs = yield from mdapilib.get_changelog(session2, pkg.pkgId)
        session2.close()

    output = {
        'changelogs': [changelog.to_json() for changelog in changelogs],
        'repo': repotype if repotype else 'release',
    }
    args = {}
    if pretty:
        args = dict(sort_keys=True, indent=4, separators=(',', ': '))

    return web.Response(
        body=json.dumps(output, **args).encode('utf-8'),
        content_type='application/json')


@asyncio.coroutine
def list_branches(request):
    ''' Return the list of all branches currently supported by mdapi
    '''
    _log.info('list_branches: %s', request)
    pretty = _get_pretty(request)
    output = sorted(list(set([
        # Remove the front part `mdapi-` and the end part -<type>.sqlite
        filename.replace('mdapi-', '').rsplit('-', 2)[0].replace(
            '-updates', '')
        for filename in os.listdir(CONFIG['DB_FOLDER'])
        if filename.startswith('mdapi') and filename.endswith('.sqlite')
    ])))

    args = {}
    if pretty:
        args = dict(sort_keys=True, indent=4, separators=(',', ': '))

    response = web.Response(body=json.dumps(output, **args).encode('utf-8'),
                            content_type='application/json')

    # The decorator doesn't work for this endpoint, so do it manually here
    # I am not really sure what doesn't work but it seems this endpoint is
    # returning an object instead of the expected generator despite it being
    # flagged as an asyncio coroutine
    url_arg = parse_qs(request.query_string)
    callback = url_arg.get('callback')
    if callback and request.method == 'GET':
        if isinstance(callback, list):
            callback = callback[0]
        response.mimetype = 'application/javascript'
        response.content_type = 'application/javascript'
        response.text = '%s(%s);' % (callback, response.text)

    return response


@asyncio.coroutine
@allows_jsonp
def process_dep(request, action):
    ''' Return the information about the packages having the specified
    action (provides, requires, obsoletes...)
    '''
    _log.info('process_dep %s: %s', action, request)
    branch = request.match_info.get('branch')
    pretty = _get_pretty(request)
    name = request.match_info.get('name')

    try:
        pkg, repotype = yield from _get_pkg(branch, name, action=action)
    except:
        raise web.HTTPBadRequest()

    output = yield from _expand_pkg_info(pkg, branch, repotype)

    args = {}
    if pretty:
        args = dict(sort_keys=True, indent=4, separators=(',', ': '))

    return web.Response(body=json.dumps(output, **args).encode('utf-8'),
                        content_type='application/json')


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
def get_conflicts(request):
    return process_dep(request, 'conflicts')


@asyncio.coroutine
def get_enhances(request):
    return process_dep(request, 'enhances')


@asyncio.coroutine
def get_recommends(request):
    return process_dep(request, 'recommends')


@asyncio.coroutine
def get_suggests(request):
    return process_dep(request, 'suggests')


@asyncio.coroutine
def get_supplements(request):
    return process_dep(request, 'supplements')


@asyncio.coroutine
def index(request):
    _log.info('index %s', request)
    return web.Response(
        body=INDEX.encode('utf-8'),
        content_type='text/html',
        charset='utf-8')


def _set_routes(app):
    routes = []
    prefix = CONFIG.get('PREFIX', '')
    if prefix:
        routes.append(('', index))

    routes.extend([
        ('/', index),
        ('/branches', list_branches),
        ('/{branch}/pkg/{name}', get_pkg),
        ('/{branch}/srcpkg/{name}', get_src_pkg),

        ('/{branch}/provides/{name}', get_provides),
        ('/{branch}/requires/{name}', get_requires),
        ('/{branch}/obsoletes/{name}', get_obsoletes),
        ('/{branch}/conflicts/{name}', get_conflicts),

        ('/{branch}/enhances/{name}', get_enhances),
        ('/{branch}/recommends/{name}', get_recommends),
        ('/{branch}/suggests/{name}', get_suggests),
        ('/{branch}/supplements/{name}', get_supplements),

        ('/{branch}/files/{name}', get_pkg_files),
        ('/{branch}/changelog/{name}', get_pkg_changelog),
    ])
    for route in routes:
        app.router.add_route('GET', prefix + route[0], route[1])
    return app


@asyncio.coroutine
def init(loop):
    logging.basicConfig()
    logging.config.dictConfig(CONFIG.get('LOGGING') or {'version': 1})

    app = web.Application(loop=loop)
    app = _set_routes(app)

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
