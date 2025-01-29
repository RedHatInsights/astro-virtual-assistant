from quart import Quart, Blueprint
from common.config import app as app_config

from routes import health
from quart_schema import QuartSchema

app = Quart(__name__)

base_url = app_config.internal_watson_extension_base_url
root = Blueprint("root", __name__, url_prefix=base_url)
root.register_blueprint(health.blueprint)

app.register_blueprint(root)
QuartSchema(app, openapi_path=base_url + "/openapi.json")

if __name__ == "__main__":
    port = int(app_config.internal_watson_extension_port)
    print(f"Starting app at port {port} with base URL: {base_url}")
    app.run(port=port)
