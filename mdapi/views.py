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

import logging
import os

from aiohttp import web

from mdapi import _get_pkg, _expand_pkg_info, _get_files, _get_changelog, CONFIG

indexfile = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'index.html')


_log = logging.getLogger(__name__)


async def index(request):
    _log.info(f'index {request}')
    return web.FileResponse(indexfile)


async def get_pkg(request):
    _log.info(f'get_pkg {request}')
    branch = request.match_info.get('branch')
    name = request.match_info.get('name')
    pkg, repotype = await _get_pkg(branch, name)

    output = await _expand_pkg_info(pkg, branch, repotype)

    return web.json_response(output)


async def get_src_pkg(request):
    _log.info(f'get_src_pkg {request}')
    branch = request.match_info.get('branch')
    name = request.match_info.get('name')
    pkg, repotype = await _get_pkg(branch, srcname=name)

    output = await _expand_pkg_info(pkg, branch, repotype)

    return web.json_response(output)


async def list_branches(request):
    ''' Return the list of all branches currently supported by mdapi
    '''
    _log.info(f'list_branches: {request}')
    output = sorted({
        # Remove the front part `mdapi-` and the end part -<type>.sqlite
        filename.replace('mdapi-', '').rsplit('-', 2)[0].replace(
            '-updates', '')
        for filename in os.listdir(CONFIG['DB_FOLDER'])
        if filename.startswith('mdapi') and filename.endswith('.sqlite')
    })

    return web.json_response(output)


async def _process_dep(request, action):
    ''' Return the information about the packages having the specified
    action (provides, requires, obsoletes...)
    '''
    _log.info(f'process_dep {action}: {request}')
    branch = request.match_info.get('branch')
    name = request.match_info.get('name')

    try:
        pkg, repotype = await _get_pkg(branch, name, action=action)
    except:
        raise web.HTTPBadRequest()

    output = await _expand_pkg_info(pkg, branch, repotype)

    return web.json_response(output)


async def get_provides(request):
    return await _process_dep(request, 'provides')


async def get_requires(request):
    return await _process_dep(request, 'requires')


async def get_obsoletes(request):
    return await _process_dep(request, 'obsoletes')


async def get_conflicts(request):
    return await _process_dep(request, 'conflicts')


async def get_enhances(request):
    return await _process_dep(request, 'enhances')


async def get_recommends(request):
    return await _process_dep(request, 'recommends')


async def get_suggests(request):
    return await _process_dep(request, 'suggests')


async def get_supplements(request):
    return await _process_dep(request, 'supplements')


async def get_pkg_files(request):
    _log.info(f'get_pkg_files {request}')
    branch = request.match_info.get('branch')
    name = request.match_info.get('name')
    pkg, repotype = await _get_pkg(branch, name)
    output = await _get_files(pkg.pkgId, branch, repotype)

    return web.json_response(output)


async def get_pkg_changelog(request):
    _log.info(f'get_pkg_changelog {request}')
    branch = request.match_info.get('branch')
    name = request.match_info.get('name')
    pkg, repotype = await _get_pkg(branch, name)
    output = await _get_changelog(pkg.pkgId, branch, repotype)

    return web.json_response(output)
