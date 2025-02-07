import injector
import quart_injector
from quart import Quart
from quart_schema import QuartSchema, RequestSchemaValidationError

from common.config import app
from common.logging import initialize_logging
from common.quart_schema import VirtualAssistantOpenAPIProvider
from common.session_storage import SessionStorage
from common.session_storage.file import FileSessionStorage
from common.session_storage.redis import RedisSessionStorage
from common.types.errors import ValidationError

from routes import api_blueprint


logger = initialize_logging()

api = Quart(__name__)

base_url = app.connector_api_base_url
api.register_blueprint(api_blueprint, url_prefix=base_url)


@api.errorhandler(RequestSchemaValidationError)
async def handle_request_validation_error(error):
    return ValidationError(message=str(error.validation_error)), 400


def configure(binder: injector.Binder) -> None:
    # Read configuration and assemble our dependencies

    # This gets injected into routes when it is requested.
    # e.g. async def status(session_storage: injector.Inject[SessionStorage]) -> TalkResponse:
    if app.session_storage == "redis":
        binder.bind(SessionStorage, to=RedisSessionStorage())

    if app.session_storage == "file":
        binder.bind(SessionStorage, to=FileSessionStorage(".va-session-storage"))


quart_injector.wire(api, configure)

QuartSchema(api, openapi_path=base_url + "/openapi.json", openapi_provider_class=VirtualAssistantOpenAPIProvider)

if __name__ == "__main__":
    port = int(app.connector_api_port)

    logger.info(f"Starting app at port {port} with base URL: {base_url}")
    api.run(port=port)
