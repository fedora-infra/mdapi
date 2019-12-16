import logging
import logging.config

from aiohttp import web
from aiohttp.web import middleware

from mdapi import CONFIG
from mdapi.views import (
        index,
        list_branches,
        get_pkg,
        get_src_pkg,
        get_provides,
        get_requires,
        get_obsoletes,
        get_conflicts,
        get_enhances,
        get_recommends,
        get_suggests,
        get_supplements,
        get_pkg_files,
        get_pkg_changelog
)

@middleware
async def add_cors_headers(request, handler):
    resp = await handler(request)
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET1'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return resp

async def init_app():
    """ Creates the aiohttp application.
        This function creates a web application configure the routes and
        returns the application object."""

    logging.basicConfig()
    logging.config.dictConfig(CONFIG.get("LOGGING") or {"version": 1})

    app = web.Application(middlewares=[add_cors_headers])

    app.add_routes([
        web.get('/', index),
        web.get('/branches', list_branches),
        web.get('/{branch}/pkg/{name}', get_pkg),
        web.get('/{branch}/srcpkg/{name}', get_src_pkg),

        web.get('/{branch}/provides/{name}', get_provides),
        web.get('/{branch}/requires/{name}', get_requires),
        web.get('/{branch}/obsoletes/{name}', get_obsoletes),
        web.get('/{branch}/conflicts/{name}', get_conflicts),

        web.get('/{branch}/enhances/{name}', get_enhances),
        web.get('/{branch}/recommends/{name}', get_recommends),
        web.get('/{branch}/suggests/{name}', get_suggests),
        web.get('/{branch}/supplements/{name}', get_supplements),

        web.get('/{branch}/files/{name}', get_pkg_files),
        web.get('/{branch}/changelog/{name}', get_pkg_changelog),
    ])

    return app
