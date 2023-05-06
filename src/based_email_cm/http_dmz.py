'''Simple HTTP service providing users with DMZ access.'''
import uuid
from datetime import timedelta

import aiofiles
import nats_nsc
from aiohttp import web

from . import config
from .common import BaseModel


class DMZCredsResponse(BaseModel):
    '''Response to a request for DMZ credentials'''
    creds: str
    username: str


class DMZHandler:
    '''Handles HTTP requests for DMZ credentials'''
    routes = web.RouteTableDef()

    @classmethod
    async def async_init(cls, cfg: config.Config):
        nsc_ctx = await nats_nsc.Context.async_factory()
        async with aiofiles.open(cfg.operator_jwt_path, mode='r') as f:
            operator = await nsc_ctx.add_operator(await f.read())
        async with aiofiles.open(cfg.dmz_account_jwt_path, mode='r') as f:
            jwt = await f.read()
        async with aiofiles.open(cfg.dmz_account_key_path, mode='r') as f:
            key = await f.read()
        account = await nsc_ctx.add_account(jwt, operator, key)
        self = cls(cfg, nsc_ctx, account, operator)
        return self

    def __init__(self, cfg: config.Config, nsc_ctx: nats_nsc.Context,
                 nsc_account: nats_nsc.common.Account,
                 nsc_operator: nats_nsc.common.Operator):
        self.cfg = cfg
        self.nsc_ctx = nsc_ctx
        self.nsc_account = nsc_account
        self.nsc_operator = nsc_operator

    async def post_creds(self, _):
        '''Handle a request for DMZ credentials'''
        username = str(uuid.uuid4())
        creds = await self.nsc_ctx.create_user(username,
                                               self.nsc_account,
                                               allow_pub=['dmz.login'],
                                               allow_sub=[f'_INBOX.{username}'],
                                               expiry=timedelta(hours=1),
                                               )

        return web.json_response(DMZCredsResponse(username=username, creds=creds.payload).dict())

    def add_routes(self, app):
        routes = [
            web.post('/creds', self.post_creds)
        ]
        app.add_routes(routes)

async def make_app(cfg: config.Config) -> web.Application:
    '''Create an aiohttp.web.Application'''
    app = web.Application()
    handler = await DMZHandler.async_init(cfg)
    handler.add_routes(app)
    return app

# handler = Handler()
# app.add_routes([web.get('/intro', handler.handle_intro),
#                 web.get('/greet/{name}', handler.handle_greeting)])
