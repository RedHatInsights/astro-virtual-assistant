import quart_injector
from quart import Quart
from quart_schema import (
    QuartSchema,
    RequestSchemaValidationError,
    Info,
    Server,
    ServerVariable,
)
import virtual_assistant.config as config

from common.logging import build_logger
from common.quart_schema import VirtualAssistantOpenAPIProvider
from common.types.errors import ValidationError
from virtual_assistant.startup import wire_routes, injector_from_config

build_logger(config.logger_type)
config.log_config()
app = Quart(__name__)

wire_routes(app)
quart_injector.wire(app, injector_from_config)


@app.errorhandler(RequestSchemaValidationError)
async def handle_request_validation_error(error):
    return ValidationError(message=str(error.validation_error)), 400


# Must happen after routes, injector, etc
QuartSchema(
    app,
    openapi_path=config.base_url + "/openapi.json",
    openapi_provider_class=VirtualAssistantOpenAPIProvider,
    info=Info(
        title="Virtual assistant",
        version="2.0.0",
        description="Virtual assistant backend service",
    ),
    servers=[
        Server(
            url=f"http://{{env}}{config.base_url}",
            description="Virtual assistant hosted services",
            variables={
                "env": ServerVariable(
                    enum=[
                        "console.redhat.com",
                        "console.stage.redhat.com",
                    ],
                    default="console.redhat.com",
                    description="Available environments",
                )
            },
        )
    ],
)

if __name__ == "__main__":
    app.run(port=config.port)
