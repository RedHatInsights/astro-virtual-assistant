import inspect
from sanic import Blueprint, response
from asyncio import CancelledError
from sanic.request import Request
from sanic.response import HTTPResponse
from typing import Text, Dict, Any, Optional, Callable, Awaitable

from rasa.core.channels.channel import (
    InputChannel,
    CollectingOutputChannel,
    UserMessage,
)

# Custom channel to read the identity header provided
# and link it to the user session
class IdentityInput(InputChannel):
    @classmethod
    def name(cls) -> Text:
        """Name of your custom channel."""
        return "identity"

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
            sender_id = request.json.get("sender")
            message = request.json.get("message")
            input_channel = self.name()
            metadata = self.get_metadata(request) # implemented below

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

        return {
            "identity": request.headers.get("x-rh-identity")
        }
