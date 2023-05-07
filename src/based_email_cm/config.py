import aiofiles
import yaml
from pydantic import Field

from based_email_cm.common import BaseModel


class Config(BaseModel):
    operator_jwt_path: str
    dmz_account_jwt_path: str | None
    dmz_account_key_path: str | None
    userspace_account_jwt_path: str | None
    userspace_account_key_path: str | None
    dmz_creds_path: str | None
    nats_url: str | None
    http_port: int = Field(default=8080)
    http_devel: bool = Field(default=False)


async def get_config(path):
    async with aiofiles.open(path, mode='r') as f:
        config_raw = yaml.safe_load(await f.read())
        return Config(**config_raw)
