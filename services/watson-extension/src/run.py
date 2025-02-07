import quart_injector
from quart import Quart
import watson_extension.config as config
from common.quart_schema import VirtualAssistantOpenAPIProvider

from quart_schema import QuartSchema

from watson_extension.startup import wire_routes, injector_from_config, injector_defaults

app = Quart(__name__)
config.log_config()

wire_routes(app)
quart_injector.wire(app, [injector_defaults, injector_from_config])

# Must happen after routes, injector, etc
QuartSchema(app, openapi_path=config.base_url + "/openapi.json", openapi_provider_class=VirtualAssistantOpenAPIProvider)

if __name__ == "__main__":
    app.run(port=config.port)
