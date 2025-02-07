from quart import Quart, Blueprint
from quart_schema import QuartSchema


def app_with_blueprint(blueprint: Blueprint) -> Quart:
    app = Quart(__name__, template_folder="../../src/watson_extension/templates")
    app.register_blueprint(blueprint)
    QuartSchema(app)  # Ensures we can return objects from the endpoints
    return app
