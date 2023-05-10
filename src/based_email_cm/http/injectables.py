from argon2 import PasswordHasher
from litestar.di import Provide

from based_email_cm import config, utils


def generate_nats_provide(cfg: config.Config) -> Provide:
    async def provide_nats_connection():
        return await utils.nats_connect(cfg)
    return Provide(provide_nats_connection)


def generate_password_hasher_provide() -> Provide:
    return Provide(PasswordHasher)
