
import aiohttp
import injector
import quart
from quart import Quart, Blueprint
from redis.asyncio import StrictRedis

from common.session_storage.redis import RedisSessionStorage
from watson_extension.auth import Authentication
from watson_extension.auth.api_key_authentication import ApiKeyAuthentication
from watson_extension.auth.no_authentication import NoAuthentication
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

@injector.provider
def redis_session_storage_provider() -> RedisSessionStorage:
    return RedisSessionStorage(StrictRedis(
        host=config.redis_hostname,
        port=config.redis_port,
        username=config.redis_username,
        password=config.redis_password,
    ))

@injector.provider
def api_key_authentication_provider() -> Authentication:
    return ApiKeyAuthentication(config.api_keys)

def injector_from_config(binder: injector.Binder) -> None:
    # Read configuration and assemble our dependencies
    binder.bind(UserIdentity, user_identity_fixed)

    # This gets injected into routes when it is requested.
    # e.g. async def status(session_storage: injector.Inject[SessionStorage]) -> StatusResponse:
    if config.session_storage == "redis":
        binder.bind(SessionStorage, to=redis_session_storage_provider)
    elif config.session_storage == "file":
        binder.bind(SessionStorage, to=FileSessionStorage(".va-session-storage"))

    if config.authentication_type == "no-auth":
        binder.bind(Authentication, to=NoAuthentication)
    elif config.authentication_type == "api-key":
        binder.bind(Authentication, to=api_key_authentication_provider)

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

    @public_root.before_request
    async def authentication_check(authentication: injector.Inject[Authentication]):
        await authentication.check_auth(quart.request)

    app.register_blueprint(public_root)
    app.register_blueprint(private_root)