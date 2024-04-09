from typing import Text
from urllib.parse import urlparse

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher

from common.requests import send_console_request


async def is_source_name_valid(tracker: Tracker, name: Text) -> bool:
    response, content = await send_console_request(
        "sources",
        "/api/sources/v3.1/graphql",
        tracker,
        method="post",
        json={
            "query": f'{{ sources(filter: {{name: "name", value: "{name}"}}){{ id, name }}}}'
        },
    )

    if response.ok and len(content.get("data").get("sources")) == 0:
        return True

    return False


async def validate_integration_url(dispatcher: CollectingDispatcher, message: Text):
    try:
        result = urlparse(message)
        if result.scheme != "https":
            dispatcher.utter_message(response="utter_integration_url_not_https")
            dispatcher.utter_message(
                response="utter_integration_setup_validation_error"
            )
            return False
    except AttributeError:
        dispatcher.utter_message(response="utter_integration_setup_validation_error")
        return False

    return True
