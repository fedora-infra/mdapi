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

from mdapi.confdata import servlogr
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


async def buildapp():
    """
    Creates an aiohttp web application
    This function creates a web application, configures the routes and returns the application
    object.
    """
    applobjc = Application(middlewares=[add_cors_headers], logger=servlogr.logrobjc)
    applobjc.add_routes(
        [
            get("/", index),
            get("/branches", list_branches),
            get("/{brch}/pkg/{name}", get_pkg),
            get("/{brch}/srcpkg/{name}", get_src_pkg),
            get("/{brch}/provides/{name}", get_provides),
            get("/{brch}/requires/{name}", get_requires),
            get("/{brch}/obsoletes/{name}", get_obsoletes),
            get("/{brch}/conflicts/{name}", get_conflicts),
            get("/{brch}/enhances/{name}", get_enhances),
            get("/{brch}/recommends/{name}", get_recommends),
            get("/{brch}/suggests/{name}", get_suggests),
            get("/{brch}/supplements/{name}", get_supplements),
            get("/{brch}/files/{name}", get_pkg_files),
            get("/{brch}/changelog/{name}", get_pkg_changelog),
        ]
    )
    return applobjc
