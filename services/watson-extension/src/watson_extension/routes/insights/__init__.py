from quart import Blueprint
from . import advisor

blueprint = Blueprint("insights", __name__, url_prefix="/insights")

blueprint.register_blueprint(advisor.blueprint)
