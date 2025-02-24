import quart_injector
from quart import Quart
import watson_extension.config as config
from common.logging import build_logger
from common.quart_schema import VirtualAssistantOpenAPIProvider

from quart_schema import QuartSchema, RequestSchemaValidationError

from common.types.errors import ValidationError
from watson_extension.startup import (
    wire_routes,
    injector_from_config,
    injector_defaults,
)

build_logger(config.logger_type)
app = Quart(__name__)
config.log_config()

wire_routes(app)
quart_injector.wire(app, [injector_defaults, injector_from_config])


@app.errorhandler(RequestSchemaValidationError)
async def handle_request_validation_error(error):
    return ValidationError(message=str(error.validation_error)), 400


# Must happen after routes, injector, etc
QuartSchema(
    app,
    openapi_path=config.base_url + "/openapi.json",
    openapi_provider_class=VirtualAssistantOpenAPIProvider,
)

if __name__ == "__main__":
    app.run(port=config.port)
