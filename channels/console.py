import inspect
from sanic import Blueprint, response
from asyncio import CancelledError
from sanic.request import Request
from sanic.response import HTTPResponse
from typing import Text, Dict, Any, Optional, Callable, Awaitable

from .identity import decode_identity

from rasa.core.channels.channel import (
    InputChannel,
    CollectingOutputChannel,
    UserMessage,
)

# Custom channel for console.redhat.com traffic
# to read the identity header provided
# and link it to the user session
class ConsoleInput(InputChannel):
    @classmethod
    def name(cls) -> Text:
        """Name of your custom channel."""
        return "console"


    def blueprint(
        self, on_new_message: Callable[[UserMessage], Awaitable[None]]
    ) -> Blueprint:

        custom_webhook = Blueprint(
            "custom_webhook_{}".format(type(self).__name__),
            inspect.getmodule(self).__name__,
        )

        @custom_webhook.route("/", methods=["GET"])
        async def health(request: Request) -> HTTPResponse:
            return response.json({"status": "ok"})

        @custom_webhook.route("/webhook", methods=["POST"])
        async def receive(request: Request) -> HTTPResponse:
            metadata = self.get_metadata(request) # implemented below

            sender_id = self.get_sender(request) # implemented below
            if not sender_id:
                return response.json({"error": "Invalid x-rh-identity header (no user_id found)"})

            message = request.json.get("message")
            input_channel = self.name()

            collector = CollectingOutputChannel()
            
            try:
                await on_new_message(
                    UserMessage(
                        message,
                        collector,
                        sender_id,
                        input_channel=input_channel,
                        metadata=metadata,
                    )
                )
            except CancelledError:
                print(
                    f"Message handling timed out for user message."
                )
            except Exception as e:
                print(
                    f"An exception occured while handling: {e}"
                )

            return response.json(collector.messages)

        return custom_webhook


    def get_metadata(self, request: Request) -> Optional[Dict[Text, Any]]:
        """Extracts the metadata from the incoming request."""

        self.identity = request.headers.get("x-rh-identity")

        return {
            "identity": self.identity
        }
    
    
    def get_sender(self, request: Request) -> Optional[Text]:
        # base64 decode the identity header
        identity_dict = decode_identity(self.identity)

        return identity_dict['identity']['user']['user_id']
