import asyncio

import uvicorn
from enum import Enum
import argparse

from based_email_cm import cli, config
from based_email_cm.http import app

ascii_banner = r'''
  _                        _                       _ _ 
 | |                      | |                     (_) |
 | |__   __ _ ___  ___  __| |  ___ _ __ ___   __ _ _| |
 | '_ \ / _` / __|/ _ \/ _` | / _ \ '_ ` _ \ / _` | | |
 | |_) | (_| \__ \  __/ (_| ||  __/ | | | | | (_| | | |
 |_.__/ \__,_|___/\___|\__,_(_)___|_| |_| |_|\__,_|_|_|
'''


class CliCommand(Enum):
    HTTP = 'http'
    ADD_ADMIN = 'add-admin'


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Based Email Login Manager',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '-c', '--config-path',
        help='Path to configuration file',
        required=True,
    )
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_http = subparsers.add_parser('http', help='Run the HTTP server')
    parser_http.set_defaults(command=CliCommand.HTTP)

    parser_admin = subparsers.add_parser('add-admin', help='Add an admin user')
    parser_admin.set_defaults(command=CliCommand.ADD_ADMIN)

    return parser


def print_banner():
    print(ascii_banner)
    print('Based Email Login Manager Service')


def run_http(config: config.Config):
    uv_app = app.create_app(config)
    uv_config = uvicorn.Config(uv_app, host='0.0.0.0', port=config.http_port)
    server = uvicorn.Server(uv_config)
    print_banner()
    server.run()


def main():
    parser = get_parser()
    args = parser.parse_args()
    config = read_config(args.config_path)
    if 'command' not in args:
        parser.print_help()
    elif args.command == CliCommand.ADD_ADMIN:
        cli.add_admin(config)
    elif args.command == CliCommand.HTTP:
        run_http(config)
    else:
        raise NotImplementedError(f'Command {args.command} not implemented')


def read_config(path: str) -> config.Config:
    return asyncio.run(config.get_config(path))


if __name__ == '__main__':
    # execute only if run as the entry point into the program
    main()
