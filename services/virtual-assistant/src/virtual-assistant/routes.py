from quart import Blueprint, jsonify, request
from quart_schema import validate_request, validate_response
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_cloud_sdk_core.api_exception import ApiException

from common.config import app
from common.auth import require_identity_header, get_org_id_from_identity
from api_types import (
    TalkRequest,
    TalkResponse,
    TalkRequestError,
    watson_response_formatter,
)


api_blueprint = Blueprint("api", __name__)


def get_watson_assistant():
    authenticator = IAMAuthenticator(app.watson_api_key)
    assistant = AssistantV2(version=app.watson_env_version, authenticator=authenticator)
    assistant.set_service_url(app.watson_api_url)
    return assistant


@api_blueprint.route("/", methods=["GET"])
async def health():
    return jsonify({"status": "Ok"})


@api_blueprint.route("/talk", methods=["POST"])
@require_identity_header
@validate_request(TalkRequest)
@validate_response(TalkResponse, 200)
@validate_response(TalkRequestError, 400)
async def talk(data: TalkRequest):
    identity = request.headers.get("x-rh-identity")
    org_id = get_org_id_from_identity(identity)

    assistant = get_watson_assistant()

    # Create session if not provided
    session_id = data.session_id
    if not session_id:
        watson_session_response = assistant.create_session(
            assistant_id=app.watson_env_id
        ).get_result()
        session_id = watson_session_response["session_id"]

    print("session_id", session_id)
    watson_input = data.input.dict(exclude_none=True)
    watson_input["message_type"] = "text"

    # Send message to Watson Assistant
    watson_message_response = None
    try:
        watson_message_response = assistant.message(
            assistant_id=app.watson_env_id,
            environment_id=app.watson_env_id,
            session_id=session_id,
            user_id=org_id,  # using org_id and user_id to identity unique users
            input=data.input.dict(exclude_none=True),
        ).get_result()
    except ApiException as e:
        return TalkRequestError(message=e.message), 400

    response = watson_response_formatter(session_id, watson_message_response)

    return response, 200
