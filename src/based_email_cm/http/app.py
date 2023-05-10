from litestar import Litestar
from litestar.config.cors import CORSConfig

from based_email_cm import config
from based_email_cm.http import injectables
from based_email_cm.http.login_controller import LoginController


def create_app(cfg: config.Config) -> Litestar:
    app = Litestar(route_handlers=[LoginController], dependencies={
        'ph': injectables.generate_password_hasher_provide(),
        'nc': injectables.generate_nats_provide(cfg),
    })
    if cfg.http_devel:
        app.cors_config = CORSConfig(allow_origins=["*"])
    return app
