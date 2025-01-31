from quart import Quart
from common.config import app
from quart_schema import QuartSchema, RequestSchemaValidationError

from routes import api_blueprint
from api_types import TalkRequestError


api = Quart(__name__)

base_url = app.connector_api_base_url
api.register_blueprint(api_blueprint, url_prefix=base_url)


@api.errorhandler(RequestSchemaValidationError)
async def handle_request_validation_error(error):
    return TalkRequestError(message=str(error.validation_error)), 400


QuartSchema(api, openapi_path=base_url + "/openapi.json")

if __name__ == "__main__":
    port = int(app.connector_api_port)
    print(f"Starting app at port {port} with base URL: {base_url}")
    api.run(port=port)
