from aiohttp import web

import asyncio

from . import config
from . import cli
from . import http_dmz

def main():
    app = asyncio.run(setup())
    web.run_app(app)

async def setup() -> web.Application:
    args = cli.get_parser().parse_args()
    cfg = await config.get_config(args.config_path)
    app = await http_dmz.make_app(cfg)
    return app

if __name__ == '__main__':
    # execute only if run as the entry point into the program
    main()
