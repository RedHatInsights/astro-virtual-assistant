import logging

import injector
from ibm_cloud_sdk_core.api_exception import ApiException
from quart import Blueprint, request
from quart_schema import validate_request, validate_response

from common.auth import get_org_id_from_identity, require_identity_header
from common.types.errors import ValidationError
from virtual_assistant.api_types import TalkRequest, TalkResponse
from virtual_assistant.watson import WatsonAssistant, format_response

blueprint = Blueprint("talk", __name__, url_prefix="/talk")

logger = logging.getLogger(__name__)

@blueprint.route("", methods=["POST"])
@require_identity_header
@validate_request(TalkRequest)
@validate_response(TalkResponse, 200)
@validate_response(ValidationError, 400)
async def talk(data: TalkRequest, assistant: injector.Inject[WatsonAssistant]) -> TalkResponse:
    identity = request.headers.get("x-rh-identity")
    org_id = get_org_id_from_identity(identity)

    # Todo: Get this from redis?
    session_id = await assistant.create_session(data.session_id)
    logger.info(f"session_id: {session_id}")

    # Send message to Watson Assistant
    try:
        watson_message_response = await assistant.send_watson_message(
            session_id=session_id,
            user_id=org_id,  # using org_id as user_id to identity unique users
            input=data.input.model_dump(exclude_none=True),
        )
    except ApiException as e:
        # Todo: Should we just let raise this error and let the handler wrap it into a validation error?
        return ValidationError(message=e.message), 400

    response = format_response(session_id, watson_message_response)
    # Todo: Check if this syntax is OK - should we update the return type to be Tuple[TalkResponse, 200] or
    # verify if the validate_response decorator adds the http code for us
    return response, 200
