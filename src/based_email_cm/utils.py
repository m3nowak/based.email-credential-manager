import nats

from based_email_cm import config


async def nats_connect(cfg: config.Config):
    return await nats.connect(cfg.nats_url, user_credentials=cfg.based_creds_path)
