from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from common.config import app

from .auth import require_identity_header, get_org_id_from_identity
from .api_types import TalkRequest


api_blueprint = Blueprint("api", __name__)

def get_watson_assistant():
    authenticator = IAMAuthenticator(app.watson_api_key)
    assistant = AssistantV2(
        version=app.watson_env_version,
        authenticator=authenticator
    )
    assistant.set_service_url(app.watson_api_url)
    return assistant


@api_blueprint.route("/", methods=["GET"])
def health():
    return jsonify({"status": "Ok"})


@api_blueprint.route("/talk", methods=["POST"])
@require_identity_header
def talk():
    data = request.get_json()
    identity = request.headers.get('x-rh-identity')
    org_id = get_org_id_from_identity(identity)

    if not data:
        return jsonify({"error": "No request body"}), 400

    try:
        validated_data = TalkRequest(**data)
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400
    
    assistant = get_watson_assistant()

    # Create session if not provided
    session_id = validated_data.metadata.session_id
    if not session_id:
        watson_session_response = assistant.create_session(
            assistant_id=app.watson_env_id
        ).get_result()
        session_id = watson_session_response['session_id']

    print("session_id", session_id)
    # Send message to Watson Assistant
    user_message = validated_data.message
    watson_message_response = assistant.message(
        assistant_id=app.watson_env_id,
        environment_id=app.watson_env_id,
        session_id = session_id,
        user_id = org_id, # using org_id and user_id to identity unique users
        input = {
            'message_type': 'text',
            'text': user_message
        }
    ).get_result()

    ## reformat watson message response to include session id and other things
    return jsonify(watson_message_response), 200
