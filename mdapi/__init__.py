# -*- coding: utf-8 -*-
#
# Copyright © 2015-2019  Red Hat, Inc.
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
import logging
import os
import re

import aiosqlite
import werkzeug.utils

from aiohttp import web

from mdapi.db import (
        GET_PACKAGE,
        GET_PACKAGE_INFO,
        GET_CO_PACKAGE,
        GET_PACKAGE_BY_SRC,
        GET_PACKAGE_BY,
        GET_FILES,
        GET_CHANGELOGS,
        Packages,
        Dependencies,
        FileList,
        ChangeLog
)


CONFIG = dict()
obj = werkzeug.utils.import_string('mdapi.default_config')
for key in dir(obj):
    if key.isupper():
        CONFIG[key] = getattr(obj, key)


if 'MDAPI_CONFIG' in os.environ and os.path.exists(os.environ['MDAPI_CONFIG']):
    with open(os.environ['MDAPI_CONFIG']) as config_file:
        exec(compile(
            config_file.read(), os.environ['MDAPI_CONFIG'], 'exec'), CONFIG)


_log = logging.getLogger(__name__)


async def _get_pkg(branch, name=None, action=None, srcname=None):
    ''' Return the pkg information for the given package in the specified
    branch or raise an aiohttp exception.
    '''
    if (not name and not srcname) or (name and srcname):
        raise web.HTTPBadRequest()

    pkg = None
    wrongdb = False
    for repotype in ['updates-testing', 'updates', 'testing', None]:
        dbfile = f'{CONFIG["DB_FOLDER"]}/mdapi-{branch}{"-"+repotype if repotype else ""}'\
                 '-primary.sqlite'

        if not os.path.exists(dbfile):
            wrongdb = True
            continue

        wrongdb = False
        async with aiosqlite.connect(f'{dbfile}') as db:
            if action:
                # It is safe to format the query since the action does not come from the
                # user.
                query = GET_PACKAGE_BY.format(action)
                async with db.execute(query, (name,)) as cursor:
                    pkgc = await cursor.fetchall()
                if pkgc:
                    pkg = [Packages(*item) for item in pkgc]
                    break
            elif srcname:
                pattern = re.compile(f"{srcname}-[0-9]")
                async with db.execute(GET_PACKAGE_BY_SRC, (srcname+'-%',)) as cursor:
                    pkgc = await cursor.fetchall()
                if pkgc:
                    for pkg_item in pkgc:
                        if pattern.match(pkg_item[3]):
                            pkg = Packages(*pkg_item)
                            break
            else:
                async with db.execute(GET_PACKAGE, (name,)) as cursor:
                    pkgc = await cursor.fetchone()
                if pkgc:
                    pkg = Packages(*pkgc)
                    break
    if wrongdb:
        raise web.HTTPBadRequest()

    if not pkg:
        raise web.HTTPNotFound()
    return (pkg, repotype)


async def _expand_pkg_info(pkgs, branch, repotype=None):
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
        dbfile = f'{CONFIG["DB_FOLDER"]}/mdapi-{branch}{"-"+repotype if repotype else ""}'\
                 '-primary.sqlite'

        async with aiosqlite.connect(f'{dbfile}') as db:
            # Fill in some extra info
            # Basic infos, always present regardless of the version of the repo
            for datatype in ['conflicts',
                             'obsoletes',
                             'provides',
                             'requires',
                             'enhances',
                             'recommends',
                             'suggests',
                             'supplements']:
                # It is safe to format the query since the datatype does not come from the
                # user.
                query = GET_PACKAGE_INFO.format(datatype)
                async with db.execute(query, (pkg.pkgKey,)) as cursor:
                    data = await cursor.fetchall()
                if data:
                    out[datatype] = [Dependencies(*item).to_json() for item in data]
                else:
                    out[datatype] = data

            # Add the list of packages built from the same src.rpm
            if pkg.rpm_sourcerpm:
                async with db.execute(GET_CO_PACKAGE, (pkg.rpm_sourcerpm,)) as cursor:
                    copkgs = await cursor.fetchall()
                out['co-packages'] = list({cpkg[2] for cpkg in copkgs})
            else:
                out['co-packages'] = []
            out['repo'] = repotype if repotype else 'release'
            output.append(out)

    if singleton:
        return output[0]
    else:
        return output


async def _get_files(pkg_id, branch, repotype):
    ''' Return the files list for the given package in the specified
    branch.
    '''
    dbfile = f'{CONFIG["DB_FOLDER"]}/mdapi-{branch}{"-"+repotype if repotype else ""}'\
             '-filelists.sqlite'
    if not os.path.exists(dbfile):
        raise web.HTTPBadRequest()

    async with aiosqlite.connect(f"{dbfile}") as db:
        async with db.execute(GET_FILES, (pkg_id,)) as cursor:
            filelists = await cursor.fetchall()

    filelists = [FileList(*item) for item in filelists]

    output = {
        'files': [fileinfo.to_json() for fileinfo in filelists],
        'repo': repotype if repotype else 'release',
    }
    return output


async def _get_changelog(pkg_id, branch, repotype):
    ''' Return the changelog for the given package in the specified
    branch.
    '''
    dbfile = f'{CONFIG["DB_FOLDER"]}/mdapi-{branch}{"-"+repotype if repotype else ""}-other.sqlite'
    if not os.path.exists(dbfile):
        raise web.HTTPBadRequest()

    async with aiosqlite.connect(f"{dbfile}") as db:
        async with db.execute(GET_CHANGELOGS, (pkg_id,)) as cursor:
            changelogs = await cursor.fetchall()

    changelogs = [ChangeLog(*item) for item in changelogs]

    output = {
        'changelogs': [changelog.to_json() for changelog in changelogs],
        'repo': repotype if repotype else 'release',
    }
    return output
