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

import os.path

from aiohttp.web import FileResponse, HTTPBadRequest, json_response

from mdapi.confdata import servlogr, standard
from mdapi.services import _expand_package_info, _get_changelog, _get_files, _get_package

homepage = os.path.join(os.path.dirname(os.path.abspath(__file__)), "homepage.html")


async def index(rqst):
    servlogr.logrobjc.info(f"index {rqst}")
    return FileResponse(homepage)


async def get_pkg(rqst):
    servlogr.logrobjc.info(f"get_pkg {rqst}")
    brch = rqst.match_info.get("brch")
    name = rqst.match_info.get("name")
    pckg, repotype = await _get_package(brch, name)
    rslt = await _expand_package_info(pckg, brch, repotype)
    return json_response(rslt)


async def get_src_pkg(rqst):
    servlogr.logrobjc.info(f"get_src_pkg {rqst}")
    brch = rqst.match_info.get("brch")
    name = rqst.match_info.get("name")
    pckg, repotype = await _get_package(brch, srcn=name)
    rslt = await _expand_package_info(pckg, brch, repotype)
    return json_response(rslt)


async def list_branches(rqst):
    """
    Return the list of all branches currently supported by mdapi
    """
    servlogr.logrobjc.info(f"list_branches {rqst}")
    rslt = sorted(
        {
            # Remove the front part `mdapi-` and the end part `-<type>.sqlite` from the filenames
            filename.replace("mdapi-", "").rsplit("-", 2)[0].replace("-updates", "")
            for filename in os.listdir(standard.DB_FOLDER)
            if filename.startswith("mdapi") and filename.endswith(".sqlite")
        }
    )
    return json_response(rslt)


async def _process_dep(rqst, actn):
    """
    Return the information about the packages having the specified action
    (as in provides, requires, obsoletes etc.)
    """
    servlogr.logrobjc.info(f"process_dep {actn} {rqst}")
    brch = rqst.match_info.get("brch")
    name = rqst.match_info.get("name")

    try:
        pckg, repotype = await _get_package(brch, name, actn=actn)
    except:  # noqa
        raise HTTPBadRequest  # noqa : B904

    rslt = await _expand_package_info(pckg, brch, repotype)
    return json_response(rslt)


async def get_provides(rqst):
    return await _process_dep(rqst, "provides")


async def get_requires(rqst):
    return await _process_dep(rqst, "requires")


async def get_obsoletes(rqst):
    return await _process_dep(rqst, "obsoletes")


async def get_conflicts(rqst):
    return await _process_dep(rqst, "conflicts")


async def get_enhances(rqst):
    return await _process_dep(rqst, "enhances")


async def get_recommends(rqst):
    return await _process_dep(rqst, "recommends")


async def get_suggests(rqst):
    return await _process_dep(rqst, "suggests")


async def get_supplements(rqst):
    return await _process_dep(rqst, "supplements")


async def get_pkg_files(rqst):
    servlogr.logrobjc.info(f"get_pkg_files {rqst}")
    brch = rqst.match_info.get("brch")
    name = rqst.match_info.get("name")
    pckg, repotype = await _get_package(brch, name)
    rslt = await _get_files(pckg.pkgId, brch, repotype)
    return json_response(rslt)


async def get_pkg_changelog(rqst):
    servlogr.logrobjc.info(f"get_pkg_changelog {rqst}")
    brch = rqst.match_info.get("brch")
    name = rqst.match_info.get("name")
    pckg, repotype = await _get_package(brch, name)
    rslt = await _get_changelog(pckg.pkgId, brch, repotype)
    return json_response(rslt)
