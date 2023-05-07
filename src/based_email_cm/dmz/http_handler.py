'''Simple HTTP service providing users with DMZ access.'''
import uuid
from datetime import timedelta

import aiofiles
import nats_nsc
from aiohttp import web

from based_email_cm import config
from based_email_cm.common import BaseModel


class DMZCredsResponse(BaseModel):
    '''Response to a request for DMZ credentials'''
    creds: str
    username: str


class HttpDmzHandler:
    '''Handles HTTP requests for DMZ credentials'''
    routes = web.RouteTableDef()

    @classmethod
    async def async_init(cls, cfg: config.Config):
        nsc_ctx = await nats_nsc.Context.async_factory()
        async with aiofiles.open(cfg.operator_jwt_path, mode='r') as f:
            operator = await nsc_ctx.add_operator(await f.read())

        if cfg.dmz_account_jwt_path is None or cfg.dmz_account_key_path is None:
            raise ValueError('DMZ configuration is required to run the DMZ service')

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
                                               allow_sub=[f'_INBOX.{username}.>'],
                                               expiry=timedelta(hours=1),
                                               )

        return web.json_response(DMZCredsResponse(username=username, creds=creds.payload).dict())

    def add_routes(self, app: web.Application):
        routes = [
            web.post('/creds', self.post_creds)
        ]
        app.add_routes(routes)

@web.middleware
async def cors(request, handler):
    response = await handler(request)
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response   

async def make_app(cfg: config.Config) -> web.Application:
    '''Create an aiohttp.web.Application'''
    middlewares = []
    if cfg.http_devel:
        middlewares.append(cors)
    app = web.Application(middlewares=middlewares)
    

    handler = await HttpDmzHandler.async_init(cfg)
    handler.add_routes(app)
    return app
