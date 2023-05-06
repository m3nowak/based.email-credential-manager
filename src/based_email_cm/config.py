import yaml
import aiofiles

from .common import BaseModel

class Config(BaseModel):
    operator_jwt_path: str
    dmz_account_jwt_path: str
    dmz_account_key_path: str

async def get_config(path):
    async with aiofiles.open(path, mode='r') as f:
        config_raw = yaml.safe_load(await f.read())
        return Config(**config_raw)
