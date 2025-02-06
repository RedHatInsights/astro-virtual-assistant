
import quart_injector
from quart import Quart, Blueprint
import config
from common.session_storage import SessionStorage
from common.session_storage.configure import configure as configure_session_storage
from common.quart_schema import VirtualAssistantOpenAPIProvider

from routes import health
from quart_schema import QuartSchema

app = Quart(__name__)

public_root = Blueprint("public_root", __name__, url_prefix=config.base_url)
private_root = Blueprint("private_root", __name__)

# Connecting private routes (/)
private_root.register_blueprint(health.blueprint)


# Connect public routes ({config.base_url})

app.register_blueprint(public_root)
app.register_blueprint(private_root)

config.log_config()

quart_injector.wire(app, configure_session_storage)

# Must happen after routes, injector, etc
QuartSchema(app, openapi_path=config.base_url + "/openapi.json", openapi_provider_class=VirtualAssistantOpenAPIProvider)

if __name__ == "__main__":
    app.run(port=config.port)
