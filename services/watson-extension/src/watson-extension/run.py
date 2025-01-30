from quart import Quart, Blueprint
import config

from routes import health
from quart_schema import QuartSchema

app = Quart(__name__)

root = Blueprint("root", __name__, url_prefix=config.base_url)
root.register_blueprint(health.blueprint)

app.register_blueprint(root)
QuartSchema(app, openapi_path=config.base_url + "/openapi.json")

if __name__ == "__main__":
    port = config.port
    print(f"Starting app at port {port} with base URL: {config.base_url}")
    app.run(port=port)
