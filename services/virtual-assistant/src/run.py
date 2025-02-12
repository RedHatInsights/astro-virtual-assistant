import quart_injector
from quart import Quart
from quart_schema import QuartSchema, RequestSchemaValidationError
import virtual_assistant.config as config

from common.logging import initialize_logging
from common.quart_schema import VirtualAssistantOpenAPIProvider
from common.types.errors import ValidationError
from virtual_assistant.startup import wire_routes, injector_from_config

initialize_logging(config.name)
config.log_config()
app = Quart(__name__)

wire_routes(app)
quart_injector.wire(app, injector_from_config)

@app.errorhandler(RequestSchemaValidationError)
async def handle_request_validation_error(error):
    return ValidationError(message=str(error.validation_error)), 400

# Must happen after routes, injector, etc
QuartSchema(app, openapi_path=config.base_url + "/openapi.json", openapi_provider_class=VirtualAssistantOpenAPIProvider)

if __name__ == "__main__":
    app.run(port=config.port)
