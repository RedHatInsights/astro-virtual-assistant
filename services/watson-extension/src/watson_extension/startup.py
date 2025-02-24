import aiohttp
import injector
import quart
import quart_injector
from quart import Quart, Blueprint
from redis.asyncio import StrictRedis

from common.session_storage.redis import RedisSessionStorage
from watson_extension.auth import Authentication
from watson_extension.auth.api_key_authentication import ApiKeyAuthentication
from watson_extension.auth.no_authentication import NoAuthentication
from watson_extension.auth.service_account_authentication import (
    ServiceAccountAuthentication,
)
from watson_extension.clients import AdvisorURL
from watson_extension.clients.aiohttp_session import aiohttp_session
from watson_extension.clients.insights.advisor import AdvisorClient, AdvisorClientHttp
from watson_extension.clients.platform_request import (
    AbstractPlatformRequest,
    DevPlatformRequest,
    PlatformRequest,
)
from watson_extension.routes import health
from watson_extension.routes import insights

import watson_extension.config as config

from common.session_storage import SessionStorage
from common.session_storage.file import FileSessionStorage
from watson_extension.clients.identity import (
    QuartUserIdentityProvider,
    AbstractUserIdentityProvider,
    FixedUserIdentityProvider,
)


@injector.provider
def dev_platform_request(
    session: injector.Inject[aiohttp.ClientSession],
) -> DevPlatformRequest:
    return DevPlatformRequest(
        session,
        refresh_token=config.dev_platform_request_offline_token,
        refresh_token_url=config.dev_platform_request_refresh_url,
    )


@injector.provider
def redis_session_storage_provider() -> RedisSessionStorage:
    return RedisSessionStorage(
        StrictRedis(
            host=config.redis_hostname,
            port=config.redis_port,
            username=config.redis_username,
            password=config.redis_password,
        )
    )


@injector.provider
def api_key_authentication_provider() -> Authentication:
    return ApiKeyAuthentication(config.api_keys)


@injector.provider
def sa_authentication_provider() -> Authentication:
    return ServiceAccountAuthentication(config.sa_client_id)


def injector_from_config(binder: injector.Binder) -> None:
    # Read configuration and assemble our dependencies
    if config.is_running_locally:
        binder.bind(
            AbstractUserIdentityProvider,
            FixedUserIdentityProvider,
            scope=injector.singleton,
        )
    else:
        # This injector is per request - as we should extract the data for each request.
        binder.bind(
            AbstractUserIdentityProvider,
            QuartUserIdentityProvider,
            scope=quart_injector.RequestScope,
        )

    if config.platform_request == "dev":
        binder.bind(
            AbstractPlatformRequest, to=dev_platform_request, scope=injector.singleton
        )
    else:
        binder.bind(
            AbstractPlatformRequest, to=PlatformRequest, scope=injector.singleton
        )

    # This gets injected into routes when it is requested.
    # e.g. async def status(session_storage: injector.Inject[SessionStorage]) -> StatusResponse:
    if config.session_storage == "redis":
        binder.bind(
            SessionStorage, to=redis_session_storage_provider, scope=injector.singleton
        )
    elif config.session_storage == "file":
        binder.bind(
            SessionStorage,
            to=FileSessionStorage(".va-session-storage"),
            scope=injector.singleton,
        )

    if config.authentication_type == "no-auth":
        binder.bind(Authentication, to=NoAuthentication, scope=injector.singleton)
    elif config.authentication_type == "api-key":
        binder.bind(
            Authentication, to=api_key_authentication_provider, scope=injector.singleton
        )
    elif config.authentication_type == "service-account":
        binder.bind(
            Authentication, to=sa_authentication_provider, scope=injector.singleton
        )

    # urls
    binder.bind(AdvisorURL, to=config.advisor_url, scope=injector.singleton)


def injector_defaults(binder: injector.Binder) -> None:
    # clients
    binder.bind(AdvisorClient, AdvisorClientHttp, scope=quart_injector.RequestScope)

    # aiohttp session
    binder.bind(aiohttp.ClientSession, aiohttp_session, scope=injector.singleton)


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
