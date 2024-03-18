from typing import List, Optional, Text
from urllib.parse import urlparse

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from common.requests import send_console_request


async def all_required_slots_are_set(
    form: FormValidationAction,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: DomainDict,
    ignore: Optional[List[Text]] = None,
) -> bool:
    for slot in await form.required_slots(
        form.domain_slots(domain), dispatcher, tracker, domain
    ):
        if ignore is not None and slot in ignore:
            continue
        if tracker.get_slot(slot) is None:
            return False

    return True


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
