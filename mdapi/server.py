import logging
import logging.config

from aiohttp import web

from mdapi import CONFIG, _set_routes


def main():

    logging.basicConfig()
    logging.config.dictConfig(CONFIG.get("LOGGING") or {"version": 1})

    app = web.Application()
    app = _set_routes(app)

    host = CONFIG.get("HOST", "127.0.0.1")
    port = CONFIG.get("PORT", 8080)

    web.run_app(app, host=host, port=port)
