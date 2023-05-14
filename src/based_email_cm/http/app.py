from litestar import Litestar
from litestar.config.cors import CORSConfig

from based_email_cm import config
from based_email_cm.http import injectables
from based_email_cm.http.login_controller import LoginController


def create_app(cfg: config.Config) -> Litestar:
    extra_kwargs = {}
    if cfg.http_devel:
        extra_kwargs['cors_config'] = CORSConfig(allow_origins=["http://localhost:4200"])
    app = Litestar(route_handlers=[LoginController], dependencies={
        'ph': injectables.generate_password_hasher_provide(),
        'nc': injectables.generate_nats_provide(cfg),
        'jwt_ctx': injectables.generate_jwt_ctx_provide(cfg),
    }, **extra_kwargs)
    
    return app
