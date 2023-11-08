import inspect
from sanic import Blueprint, response
from asyncio import CancelledError
from sanic.request import Request
from sanic.response import HTTPResponse
from typing import Text, Dict, Any, Optional, Callable, Awaitable

from common import decode_identity
from common import logging

from rasa.core.channels.channel import (
    InputChannel,
    CollectingOutputChannel,
    UserMessage,
)

logger = logging.initialize_logging()


# Custom channel for console.redhat.com traffic
# to read the identity header provided
# and link it to the user session
class ConsoleInput(InputChannel):
    @classmethod
    def name(cls) -> Text:
        """Base of the API path"""
        return "/api/virtual-assistant/v1"

    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[None]]
    ) -> Blueprint:
        custom_webhook = Blueprint("custom_webhook_{}".format(type(self).__name__))

        @custom_webhook.route("/", methods=["GET"])
        async def health(request: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @custom_webhook.route("/openapi.json", methods=["GET"])
        async def openapi(request: Request) -> HTTPResponse:
            return await response.file("openapi.json")

        @custom_webhook.route("/talk", methods=["POST"])
        async def receive(request: Request) -> HTTPResponse:
            identity = self.extract_identity(request)
            if not identity:
                return response.json(
                    {"error": "No x-rh-identity header present"}, status=400
                )
            
            is_org_admin = self.extract_is_org_admin(identity, request)

            current_url = self.extract_current_url(request)  # not a required field

            sender_id = self.get_sender(identity)
            if not sender_id:
                return response.json(
                    {"error": "Invalid x-rh-identity header (org_id and username not found)"},
                    status=400,
                )

            if not request.json:
                return response.json({"error": "Invalid body"}, status=400)

            message = request.json.get("message")
            if not message:
                return response.json({"error": "Invalid json body"}, status=400)

            input_channel = self.name()

            collector = CollectingOutputChannel()

            try:
                await on_new_message(
                    UserMessage(
                        message,
                        collector,
                        sender_id,
                        input_channel=input_channel,
                        metadata=self.build_metadata(identity, is_org_admin, current_url),
                    )
                )
            except CancelledError:
                logger.error("Message handling timed out for user message.")
            except Exception as e:
                logger.error(
                    "An exception occured while handling a message: %s",
                    e,
                )

                logger.debug("Message: %s", message)

            return response.json(collector.messages)

        return custom_webhook

    def extract_identity(self, request: Request) -> Optional[Dict[Text, Any]]:
        """Extracts the identity from the incoming request."""
        identity = request.headers.get("x-rh-identity")
        return identity
    
    def extract_is_org_admin(self, identity, request: Request):
        # base64 decode the identity header
        identity_dict = decode_identity(identity)

        is_org_admin = False
        try:
            is_org_admin = identity_dict["identity"]["user"]["is_org_admin"]
        except KeyError:
            return False
        
        return is_org_admin

    def extract_current_url(self, request: Request) -> Optional[Dict[Text, Any]]:
        """Extracts the current url from the incoming request."""
        if request.json.get("metadata"):
            return request.json.get("metadata").get("current_url")

        return None

    def get_sender(self, identity) -> Optional[Text]:
        # base64 decode the identity header
        identity_dict = decode_identity(identity)

        org_id = None
        username = None
        try:
            org_id = identity_dict["identity"]["org_id"] # should use top level org_id
            username = identity_dict["identity"]["user"]["username"]
        except KeyError:
            return None
        if org_id and username:
            return "{org_id}-{username}".format(org_id=org_id, username=username)

        return None

    def build_metadata(self, identity, is_org_admin, current_url) -> Dict[Text, Any]:
        return {"identity": identity, "is_org_admin": is_org_admin, "current_url": current_url}
