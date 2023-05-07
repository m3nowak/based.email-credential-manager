import asyncio

import aiofiles
import nats
import nats.aio.client
import nats.js.client
import nats_nsc

from based_email_cm import config

class NatsDMZHandler():
    @classmethod
    async def async_init(cls, cfg: config.Config):
        nsc_ctx = await nats_nsc.Context.async_factory()
        async with aiofiles.open(cfg.operator_jwt_path, mode='r') as f:
            operator = await nsc_ctx.add_operator(await f.read())

        if cfg.userspace_account_jwt_path is None or cfg.userspace_account_key_path is None:
            raise ValueError('Userspace configuration is required to run the NATS DMZ service')
        
        if cfg.dmz_creds_path is None:
            raise ValueError('DMZ credentials are required to run the NATS DMZ service')

        if cfg.nats_url is None:
            raise ValueError('NATS URL is required to run the NATS DMZ service')
        

        async with aiofiles.open(cfg.userspace_account_jwt_path, mode='r') as f:
            jwt = await f.read()
        async with aiofiles.open(cfg.userspace_account_key_path, mode='r') as f:
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
        self.creds_path:str = cfg.dmz_creds_path #type:ignore
        self.nats_url:str = cfg.nats_url #type:ignore
        self.nc: nats.aio.client.Client = None #type:ignore
        self.js: nats.js.client.JetStreamContext = None #type:ignore
        self.subs = []

    async def set_up(self):
        self.nc = await nats.connect(self.nats_url, user_credentials=self.creds_path)
        self.js = self.nc.jetstream()
    
    @staticmethod
    async def login_request(nc: nats.aio.client.Client, msg):
        print(f"Received a message on '{msg.subject} {msg.reply}': {msg.data.decode()}")
        await nc.publish(msg.reply, b'I can help')

    async def run(self):
        async def lr_p(msg):
            await self.login_request(self.nc, msg)
        
        sub = await self.nc.subscribe("dmz.login", "", lr_p)
        self.subs.append(sub)
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.exceptions.CancelledError:
            print("Bye!")
            await self.tear_down()
    
    async def tear_down(self):
        for sub in self.subs:
            await sub.unsubscribe()
        await self.nc.close()
