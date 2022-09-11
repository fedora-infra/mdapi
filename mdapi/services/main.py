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

from aiohttp.web import Application, HTTPException, get, middleware

from mdapi.confdata.servlogr import logrobjc
from mdapi.confdata.standard import (  # noqa
    CRON_SLEEP,
    DB_FOLDER,
    DL_SERVER,
    DL_VERIFY,
    KOJI_REPO,
    PKGDB2_URL,
    PKGDB2_VERIFY,
    PUBLISH_CHANGES,
    repomd_xml_namespace,
)
from mdapi.services.appviews import (
    get_conflicts,
    get_enhances,
    get_obsoletes,
    get_pkg,
    get_pkg_changelog,
    get_pkg_files,
    get_provides,
    get_recommends,
    get_requires,
    get_src_pkg,
    get_suggests,
    get_supplements,
    index,
    list_branches,
)


@middleware
async def add_cors_headers(request, handler):
    try:
        response = await handler(request)
    except HTTPException as excp:
        excp.headers["Access-Control-Allow-Origin"] = "*"
        excp.headers["Access-Control-Allow-Methods"] = "GET"
        raise
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET"
    return response


def buildapp():
    """
    Creates an aiohttp web application
    This function creates a web application, configures the routes and returns the application
    object.
    """
    applobjc = Application(middlewares=[add_cors_headers], logger=logrobjc)
    applobjc.add_routes(
        [
            get("/", index),
            get("/branches", list_branches),
            get("/{branch}/pkg/{name}", get_pkg),
            get("/{branch}/srcpkg/{name}", get_src_pkg),
            get("/{branch}/provides/{name}", get_provides),
            get("/{branch}/requires/{name}", get_requires),
            get("/{branch}/obsoletes/{name}", get_obsoletes),
            get("/{branch}/conflicts/{name}", get_conflicts),
            get("/{branch}/enhances/{name}", get_enhances),
            get("/{branch}/recommends/{name}", get_recommends),
            get("/{branch}/suggests/{name}", get_suggests),
            get("/{branch}/supplements/{name}", get_supplements),
            get("/{branch}/files/{name}", get_pkg_files),
            get("/{branch}/changelog/{name}", get_pkg_changelog),
        ]
    )
    return applobjc
