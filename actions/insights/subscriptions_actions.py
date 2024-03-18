from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ActionExecuted, UserUtteranceReverted

from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match
from common import logging
from common.requests import send_console_request

logger = logging.initialize_logging()

CATEGORY_ACTIVE = "active"
CATEGORY_EXPIRED = "expired"
CATEGORY_EXPIRING = "expiring"

subs_categories = FuzzySlotMatch(
    "subscriptions_category",
    [
        FuzzySlotMatchOption(CATEGORY_ACTIVE),
        FuzzySlotMatchOption(CATEGORY_EXPIRED),
        FuzzySlotMatchOption(CATEGORY_EXPIRING),
    ],
)


class SubscriptionsCheck(Action):

    def name(self) -> Text:
        return "action_check_subscriptions"

    def cancel(self, dispatcher: CollectingDispatcher):
        dispatcher.utter_message(response="utter_unknown_topic")
        return [UserUtteranceReverted()]

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        user_input = tracker.latest_message["text"]

        resolved = []
        for word in user_input.split(" "):
            resolved = resolve_slot_match(word, subs_categories)

            if len(resolved) > 0:
                break

        response, content = await send_console_request(
            "rhsm", "/api/rhsm/v2/products/status", tracker
        )

        if not response.ok:
            return self.cancel(dispatcher)

        if resolved.get("subscriptions_category"):
            resolved_category = resolved["subscriptions_category"]
            resolved_category_text = resolved["subscriptions_category"]

            if resolved_category == CATEGORY_EXPIRING:
                resolved_category = "expiringSoon"

            content_body = content.get("body")
            subs_type_count = content_body.get(resolved_category)

            if content_body:
                response_text = (
                    f"You have {subs_type_count} {resolved_category_text} subscriptions"
                )
                dispatcher.utter_message(text=response_text)
        else:
            content_body = content.get("body")
            if content_body:
                response_text = f"You have:\n{content_body['active']} active subscriptions\n{content_body['expiringSoon']} subscriptions that are expiring soon\n{content_body['expired']} that have alredy expired"
                dispatcher.utter_message(text=response_text)
