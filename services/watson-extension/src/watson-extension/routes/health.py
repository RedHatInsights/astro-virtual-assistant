import enum
from dataclasses import dataclass

from quart import Blueprint
from quart_schema import validate_response

blueprint = Blueprint("health", __name__, url_prefix="/health")

class Status(enum.Enum):
    """
    Enumeration of possible states 'ok' or 'error'
    """
    OK = 'ok'
    ERROR = 'error'

@dataclass
class StatusResponse:
    """ Status of the application """

    status: Status

@blueprint.get("/status")
@validate_response(StatusResponse)
async def status() -> StatusResponse:
    """
    Returns the current status of the application
    """
    return StatusResponse(status=Status.OK)
