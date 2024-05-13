from typing import Any, Text, Dict, List

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions.actions import all_required_slots_are_set
from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match
from common import logging


logger = logging.initialize_logging()

product_kind = FuzzySlotMatch(
    "insights_product_kind",
    [
        FuzzySlotMatchOption("ansible"),
        FuzzySlotMatchOption("rhel", ["rhel", "redhat", "red-hat", "red hat"]),
        FuzzySlotMatchOption("openshift", ["openshift", "open shift"]),
    ],
)


class InsightsGeneralSetup(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_setup_insights"

    async def extract_insights_product_kind(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        requested_slot = tracker.get_slot("requested_slot")
        user_input = tracker.latest_message["text"]

        if (requested_slot == "insights_product_kind") or (
            requested_slot is None and tracker.get_slot("insights_product_kind") is None
        ):
            resolved = self.resolve_insights_product_kind(user_input)
            if len(resolved) > 0:
                return resolved

        return {}

    async def validate_insights_product_kind(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"insights_product_kind": slot_value}

    def resolve_insights_product_kind(self, user_input):
        for word in user_input.split(" "):
            resolved = resolve_slot_match(word, product_kind)
            if len(resolved) > 0:
                return resolved

        return {}

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        events = await super().run(dispatcher, tracker, domain)

        if await all_required_slots_are_set(self, dispatcher, tracker, domain):
            slot_value = tracker.get_slot("insights_product_kind")
            if slot_value == "ansible":
                dispatcher.utter_message(response="utter_ansible_activation_guide")
            elif slot_value == "openshift":
                dispatcher.utter_message(response="utter_openshift_docs")
            else:
                dispatcher.utter_message(response="utter_rhel_config_guide")

        return events
