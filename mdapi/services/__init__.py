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
import re

import aiosqlite
from aiohttp.web import HTTPBadRequest, HTTPNotFound

from mdapi.confdata import standard
from mdapi.database.sqlq import (
    GET_CHANGELOGS,
    GET_CO_PACKAGE,
    GET_FILES,
    GET_PACKAGE,
    GET_PACKAGE_BY,
    GET_PACKAGE_BY_SRC,
    GET_PACKAGE_INFO,
)
from mdapi.services.apimodel import ChangeLog, Dependencies, FileList, Packages


async def _get_package(brch, name=None, actn=None, srcn=None):
    """
    Return the package information for the given package in the specified branch or raise an
    aiohttp exception
    """
    if (not name and not srcn) or (name and srcn):
        raise HTTPBadRequest()

    pckg = None
    wrongdbs = False

    for repotype in ["updates-testing", "updates", "testing", None]:
        if repotype:
            dtbsfile = f"{standard.DB_FOLDER}/mdapi-{brch}-{repotype}-primary.sqlite"
        else:
            dtbsfile = f"{standard.DB_FOLDER}/mdapi-{brch}-primary.sqlite"

        if not os.path.exists(dtbsfile):
            wrongdbs = True
            continue

        wrongdbs = False
        async with aiosqlite.connect(dtbsfile) as dtbsobjc:
            if actn:
                """
                It is safe to format the query since the action does not come from the user.
                """
                sqlquery = GET_PACKAGE_BY.format(actn)
                async with dtbsobjc.execute(sqlquery, (name,)) as dbcursor:
                    pkgc = await dbcursor.fetchall()
                if pkgc:
                    pckg = [Packages(*item) for item in pkgc]
                    break
            elif srcn:
                async with dtbsobjc.execute(GET_PACKAGE_BY_SRC, (f"{srcn}-%",)) as dbcursor:
                    pkgc = await dbcursor.fetchall()
                if pkgc:
                    for pkgx in pkgc:
                        # Try to match the package with the source name at first
                        if pkgx[2] == srcn:
                            pckg = Packages(*pkgx)
                            break

                    if pckg:
                        break

                    srcn = re.escape(srcn)
                    ptrn = re.compile(f"{srcn}-[0-9]")
                    for pkgx in pkgc:
                        if ptrn.match(pkgx[3]):
                            pckg = Packages(*pkgx)
                            break
            else:
                async with dtbsobjc.execute(GET_PACKAGE, (name,)) as dbcursor:
                    pkgc = await dbcursor.fetchone()
                if pkgc:
                    pckg = Packages(*pkgc)
                    break

    if wrongdbs:
        raise HTTPBadRequest()

    if not pckg:
        raise HTTPNotFound()

    return (pckg, repotype)


async def _expand_package_info(pkgs, brch, repotype):
    """
    Return a JSON blob containing all the information we want to return for the provided package
    or packages
    """
    singletonset = False

    if not isinstance(pkgs, (list, tuple)):
        singletonset = True
        pkgs = [pkgs]

    rslt = []

    for pkgx in pkgs:
        otpt = pkgx.to_json()
        if repotype:
            dtbsfile = f"{standard.DB_FOLDER}/mdapi-{brch}-{repotype}-primary.sqlite"
        else:
            dtbsfile = f"{standard.DB_FOLDER}/mdapi-{brch}-primary.sqlite"

        async with aiosqlite.connect(dtbsfile) as dtbsobjc:
            """
            Fill in some extra info
            Basic information is always present regardless of the version of the repository
            """
            for datatype in [
                "conflicts",
                "obsoletes",
                "provides",
                "requires",
                "enhances",
                "recommends",
                "suggests",
                "supplements",
            ]:
                """
                It is safe to format the query since the datatype does not come from the user.
                """
                sqlquery = GET_PACKAGE_INFO.format(datatype)
                async with dtbsobjc.execute(sqlquery, (pkgx.pkgKey,)) as dbcursor:
                    data = await dbcursor.fetchall()
                    if data:
                        otpt[datatype] = [Dependencies(*item).to_json() for item in data]
                    else:
                        otpt[datatype] = data

            """
            Add the list of packages built from the same src.rpm
            """
            if pkgx.rpm_sourcerpm:
                async with dtbsobjc.execute(GET_CO_PACKAGE, (pkgx.rpm_sourcerpm,)) as dbcursor:
                    cosrcpkg = await dbcursor.fetchall()
                otpt["co-packages"] = [cpkg[0] for cpkg in cosrcpkg]
            else:
                otpt["co-packages"] = []
            otpt["repo"] = repotype if repotype else "release"
            rslt.append(otpt)

    if singletonset:
        return rslt[0]
    else:
        return rslt


async def _get_files(pkid, brch, repotype):
    """
    Return the list of files for the given package in the specified branch.
    """
    if repotype:
        dtbsfile = f"{standard.DB_FOLDER}/mdapi-{brch}-{repotype}-filelists.sqlite"
    else:
        dtbsfile = f"{standard.DB_FOLDER}/mdapi-{brch}-filelists.sqlite"

    if not os.path.exists(dtbsfile):
        raise HTTPBadRequest()

    async with aiosqlite.connect(dtbsfile) as dtbsobjc:
        async with dtbsobjc.execute(GET_FILES, (pkid,)) as dbcursor:
            filelist = await dbcursor.fetchall()

    filelist = [FileList(*item) for item in filelist]

    rslt = {
        "files": [fileinfo.to_json() for fileinfo in filelist],
        "repo": repotype if repotype else "release",
    }

    return rslt


async def _get_changelog(pkid, brch, repotype):
    """
    Return the changelog for the given packages in the specified branch.
    """
    if repotype:
        dtbsfile = f"{standard.DB_FOLDER}/mdapi-{brch}-{repotype}-other.sqlite"
    else:
        dtbsfile = f"{standard.DB_FOLDER}/mdapi-{brch}-other.sqlite"

    if not os.path.exists(dtbsfile):
        raise HTTPBadRequest()

    async with aiosqlite.connect(dtbsfile) as dtbsfile:
        async with dtbsfile.execute(GET_CHANGELOGS, (pkid,)) as dbcursor:
            changeloglist = await dbcursor.fetchall()

    changeloglist = [ChangeLog(*item) for item in changeloglist]

    rslt = {
        "changelogs": [changelog.to_json() for changelog in changeloglist],
        "repo": repotype if repotype else "release",
    }

    return rslt
