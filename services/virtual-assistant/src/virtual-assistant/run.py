import quart_injector
from quart import Quart
from quart_schema import QuartSchema, RequestSchemaValidationError

from common.session_storage.configure import configure as configure_session_storage
from common.config import app
from common.logging import initialize_logging
from common.quart_schema import VirtualAssistantOpenAPIProvider
from common.types.errors import ValidationError

from routes import api_blueprint


logger = initialize_logging()

api = Quart(__name__)

base_url = app.connector_api_base_url
api.register_blueprint(api_blueprint, url_prefix=base_url)


@api.errorhandler(RequestSchemaValidationError)
async def handle_request_validation_error(error):
    return ValidationError(message=str(error.validation_error)), 400


quart_injector.wire(api, configure_session_storage)

QuartSchema(api, openapi_path=base_url + "/openapi.json", openapi_provider_class=VirtualAssistantOpenAPIProvider)

if __name__ == "__main__":
    port = int(app.connector_api_port)

    logger.info(f"Starting app at port {port} with base URL: {base_url}")
    api.run(port=port)
