import injector
from quart import Quart, Blueprint
from redis.asyncio import StrictRedis

from common.session_storage.redis import RedisSessionStorage
from common.session_storage import SessionStorage
from common.session_storage.file import FileSessionStorage

import virtual_assistant.config as config
from virtual_assistant.routes import health
from virtual_assistant.routes import talk
from virtual_assistant.watson import (
    WatsonAssistant,
    WatsonAssistantImpl,
    build_assistant,
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
def watson_provider() -> WatsonAssistant:
    return WatsonAssistantImpl(
        assistant=build_assistant(
            config.watson_api_key, config.watson_env_version, config.watson_api_url
        ),
        assistant_id=config.watson_env_id,  # Todo: Should we use a different id for the assistant?
        environment_id=config.watson_env_id,
    )


def injector_from_config(binder: injector.Binder) -> None:
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

    binder.bind(WatsonAssistant, to=watson_provider, scope=injector.singleton)


def wire_routes(app: Quart) -> None:
    public_root = Blueprint("public_root", __name__, url_prefix=config.base_url)
    private_root = Blueprint("private_root", __name__)

    # Connecting private routes (/)
    private_root.register_blueprint(health.blueprint)

    # Connect public routes ({config.base_url})
    public_root.register_blueprint(talk.blueprint)

    app.register_blueprint(public_root)
    app.register_blueprint(private_root)
