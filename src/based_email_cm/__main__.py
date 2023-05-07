import asyncio

from aiohttp import web

from based_email_cm import cli, config
from based_email_cm.dmz import http_handler, nats_handler

ascii_banner = r'''
  _                        _                       _ _ 
 | |                      | |                     (_) |
 | |__   __ _ ___  ___  __| |  ___ _ __ ___   __ _ _| |
 | '_ \ / _` / __|/ _ \/ _` | / _ \ '_ ` _ \ / _` | | |
 | |_) | (_| \__ \  __/ (_| ||  __/ | | | | | (_| | | |
 |_.__/ \__,_|___/\___|\__,_(_)___|_| |_| |_|\__,_|_|_|
'''


def print_banner():
    print(ascii_banner)
    print('Based Email Credential Manager Service')


async def run_nats_dmz(config: config.Config):
    handler = await nats_handler.NatsDMZHandler.async_init(config)
    await handler.set_up()
    print('NATS DMZ service running')

    await handler.run()


def main():
    args = cli.get_parser().parse_args()
    if args.http_dmz and args.nats_dmz:
        raise ValueError('Only one of --http-dmz and --nats-dmz can be specified')
    print_banner()
    config = read_config(args.config_path)
    if args.http_dmz:
        app = asyncio.run(http_handler.make_app(config))
        web.run_app(app, port=config.http_port)
    if args.nats_dmz:
        asyncio.run(run_nats_dmz(config))
        


def read_config(path: str) -> config.Config:
    return asyncio.run(config.get_config(path))


if __name__ == '__main__':
    # execute only if run as the entry point into the program
    main()
