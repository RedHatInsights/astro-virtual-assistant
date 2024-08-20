from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted
from rasa_sdk.types import DomainDict

from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match
from common import logging
from common.requests import send_console_request

logger = logging.initialize_logging()

SUBS_PRODUCT_TYPE_SLOT = "subs_product_type"

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

subs_product_type_categories = FuzzySlotMatch(
    "subs_product_type",
    [
        FuzzySlotMatchOption("openshift", ["openshift", "open shift"]),
        FuzzySlotMatchOption("rhel", ["rhel", "red hat enterprise linux", "linux"]),
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
            logger.debug(
                "Failed to get a response from the RHSM API: status {}; result {}".format(
                    response.status, content
                )
            )
            return self.cancel(dispatcher)

        if resolved.get("subscriptions_category"):
            resolved_category = resolved["subscriptions_category"]
            resolved_category_text = resolved["subscriptions_category"]

            if resolved_category == CATEGORY_EXPIRING:
                resolved_category = "expiringSoon"

            content_body = content.get("body")
            subs_type_count = content_body.get(resolved_category)

            if content_body:
                dispatcher.utter_message(
                    response="utter_subscriptions_count_granular",
                    count=subs_type_count,
                    category=resolved_category_text,
                )
        else:
            content_body = content.get("body")
            if content_body:
                dispatcher.utter_message(
                    response="utter_subscriptions_count_all",
                    active=content_body["active"],
                    expiring=content_body["expiringSoon"],
                    expired=content_body["expired"],
                )


class SubsProductUsage(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_subs_product_usage"

    @staticmethod
    def extract_subs_product_type(
        dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == SUBS_PRODUCT_TYPE_SLOT:
            resolved = resolve_slot_match(
                tracker.latest_message["text"], subs_product_type_categories
            )

            if len(resolved) > 0:
                return resolved

            return {SUBS_PRODUCT_TYPE_SLOT: None}

        return {}

    @staticmethod
    def validate_subs_product_type(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {SUBS_PRODUCT_TYPE_SLOT: value}

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        events = await super().run(dispatcher, tracker, domain)

        requested_slot = tracker.get_slot("requested_slot")

        if requested_slot == SUBS_PRODUCT_TYPE_SLOT:
            product_type = tracker.get_slot(SUBS_PRODUCT_TYPE_SLOT)
            if product_type == "rhel":
                dispatcher.utter_message(response="utter_subs_product_usage_rhel_page")
            elif product_type == "openshift":
                dispatcher.utter_message(
                    response="utter_subs_product_usage_openshift_page"
                )

        return events
