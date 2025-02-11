import aiohttp
import injector
from quart import Quart, Blueprint

from common.session_storage.redis import RedisSessionStorage
from watson_extension.clients import AdvisorURL
from watson_extension.clients.aiohttp_session import aiohttp_session
from watson_extension.clients.insights.advisor import AdvisorClient, AdvisorClientHttp
from watson_extension.clients.platform_request import PlatformRequest
from watson_extension.routes import health
from watson_extension.routes import insights

import watson_extension.config as config

from common.session_storage import SessionStorage
from common.session_storage.file import FileSessionStorage
from watson_extension.clients.identity import UserIdentity, user_identity_fixed

def injector_from_config(binder: injector.Binder) -> None:
    # Read configuration and assemble our dependencies
    binder.bind(UserIdentity, user_identity_fixed)

    # This gets injected into routes when it is requested.
    # e.g. async def status(session_storage: injector.Inject[SessionStorage]) -> StatusResponse:
    if config.session_storage == "redis":
        binder.bind(SessionStorage, to=RedisSessionStorage())
    elif config.session_storage == "file":
        binder.bind(SessionStorage, to=FileSessionStorage(".va-session-storage"))

    # urls
    binder.bind(AdvisorURL, to="http://localhost/")

def injector_defaults(binder: injector.Binder) -> None:
    # clients
    binder.bind(AdvisorClient, AdvisorClientHttp)

    # platform request
    binder.bind(PlatformRequest, PlatformRequest)

    # aiohttp session
    binder.bind(aiohttp.ClientSession, aiohttp_session)

def wire_routes(app: Quart) -> None:
    public_root = Blueprint("public_root", __name__, url_prefix=config.base_url)
    private_root = Blueprint("private_root", __name__)

    # Connecting private routes (/)
    private_root.register_blueprint(health.blueprint)

    # Connect public routes ({config.base_url})
    public_root.register_blueprint(insights.blueprint)

    app.register_blueprint(public_root)
    app.register_blueprint(private_root)