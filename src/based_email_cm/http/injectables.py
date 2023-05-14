from argon2 import PasswordHasher
from litestar.di import Provide

from based_email_cm import config, utils, jwt_ctx


def generate_nats_provide(cfg: config.Config) -> Provide:
    async def provide_nats_connection():
        return await utils.nats_connect(cfg)
    return Provide(provide_nats_connection)

def generate_jwt_ctx_provide(cfg: config.Config) -> Provide:
    def provide_jwt_ctx():
        return jwt_ctx.JwtCtx.from_config(cfg)
    return Provide(provide_jwt_ctx, sync_to_thread=True)

def generate_password_hasher_provide() -> Provide:
    return Provide(PasswordHasher, sync_to_thread=True)
