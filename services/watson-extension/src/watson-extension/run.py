from quart import Quart, Blueprint, logging
import config

from routes import health
from quart_schema import QuartSchema

app = Quart(__name__)

root = Blueprint("root", __name__, url_prefix=config.base_url)
root.register_blueprint(health.blueprint)

app.register_blueprint(root)
QuartSchema(app, openapi_path=config.base_url + "/openapi.json")

config.log_config()

if __name__ == "__main__":
    app.run(port=config.port)
