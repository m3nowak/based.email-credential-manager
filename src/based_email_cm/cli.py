import getpass
import asyncio
from datetime import datetime

from argon2 import PasswordHasher

from based_email_cm import models, utils, config


async def _add_admin(username: str, password: str, email: str, ph: PasswordHasher, cfg: config.Config):
    user = models.User(username=username, password_hash=ph.hash(password),
                       email=email,  # pyright: ignore[reportGeneralTypeIssues]
                       is_superuser=True, date_joined=datetime.now())
    nc = await utils.nats_connect(cfg)
    js = nc.jetstream()
    user_id_map_bucket, user_bucket = await asyncio.gather(
        js.key_value(models.USER_MAP_BUCKET),
        js.key_value(models.USER_BUCKET)
    )
    await asyncio.gather(
        user_id_map_bucket.put(username, str(user.id).encode('utf-8')),
        user_bucket.put(str(user.id), user.json().encode('utf-8'))
    )
    await nc.close()
    print("Admin added!")


def add_admin(cfg: config.Config):
    username = input("Enter username:")
    password = getpass.getpass("Enter password:")
    email = input("Enter email:")
    asyncio.run(_add_admin(username, password, email, PasswordHasher(), cfg))
