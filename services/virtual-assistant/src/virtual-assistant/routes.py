from quart import Blueprint, jsonify, request
from quart_schema import validate_request, validate_response
from ibm_cloud_sdk_core.api_exception import ApiException

from common.logging import initialize_logging
from common.auth import require_identity_header, get_org_id_from_identity
from common.types.errors import ValidationError
from api_types import (
    TalkRequest,
    TalkResponse,
)
from watson import WatsonAssistant


logger = initialize_logging()

api_blueprint = Blueprint("api", __name__)

assistant = WatsonAssistant()


@api_blueprint.route("/", methods=["GET"])
async def health():
    return jsonify({"status": "Ok"})


@api_blueprint.route("/talk", methods=["POST"])
@require_identity_header
@validate_request(TalkRequest)
@validate_response(TalkResponse, 200)
@validate_response(ValidationError, 400)
async def talk(data: TalkRequest) -> TalkResponse:
    identity = request.headers.get("x-rh-identity")
    org_id = get_org_id_from_identity(identity)

    assistant.authenticate()

    session_id = assistant.create_session(data.session_id)
    logger.info(f"session_id: {session_id}")

    # Send message to Watson Assistant
    watson_message_response = None
    try:
        watson_message_response = assistant.send_watson_message(
            session_id=session_id,
            org_id=org_id,  # using org_id as user_id to identity unique users
            input=data.input.dict(exclude_none=True),
        )
    except ApiException as e:
        return ValidationError(message=e.message), 400

    response = assistant.format_response(session_id, watson_message_response)

    return response, 200
