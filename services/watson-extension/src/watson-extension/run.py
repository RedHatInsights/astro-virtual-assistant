import injector
import quart_injector
from quart import Quart, Blueprint
import config
from common.config import app as app_config
from common.session_storage import SessionStorage
from common.session_storage.file import FileSessionStorage
from common.session_storage.redis import RedisSessionStorage
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

def configure(binder: injector.Binder) -> None:
    # Read configuration and assemble our dependencies

    # This gets injected into routes when it is requested.
    # e.g. async def status(session_storage: injector.Inject[SessionStorage]) -> StatusResponse:
    if app_config.session_storage == "redis":
        binder.bind(SessionStorage, to=RedisSessionStorage())

    if app_config.session_storage == "file":
        binder.bind(SessionStorage, to=FileSessionStorage(".va-session-storage"))

quart_injector.wire(app, configure)

# Must happen after routes, injector, etc
QuartSchema(app, openapi_path=config.base_url + "/openapi.json", openapi_provider_class=VirtualAssistantOpenAPIProvider)

if __name__ == "__main__":
    app.run(port=config.port)
