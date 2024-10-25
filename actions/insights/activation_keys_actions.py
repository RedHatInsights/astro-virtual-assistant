import re
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    ActionExecuted,
    SlotSet,
)
from rasa_sdk.types import DomainDict

from actions.actions import form_action_is_starting
from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match

from common import logging
from common.header import Header
from common.metrics import (
    flow_started_count,
    Flow,
    flow_finished_count,
    action_custom_action_count,
)
from common.requests import send_console_request


logger = logging.initialize_logging()

ACTIVATION_KEY_NAME = "inventory_activation_key_name"

class ValidateFormActivationKeyCreate(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_inventory_create_activation_key"

    @staticmethod
    def extract_inventory_activation_key_name(
        dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == ACTIVATION_KEY_NAME:
            name = tracker.latest_message.get("text").replace(" ", "_")
            return {ACTIVATION_KEY_NAME: name}

        return {}

    @staticmethod
    def validate_image_builder_rhel_version(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        # must contain only numbers, letters, underscores, and hyphens.
        pattern = r'^[a-zA-Z0-9_-]+$'
        if not value or re.match(pattern, value):
            dispatcher.utter_message(response="utter_inventory_activation_key_name_invalid")
            return {ACTIVATION_KEY_NAME: None}
        return {ACTIVATION_KEY_NAME: value}

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        if await form_action_is_starting(self, dispatcher, tracker, domain):
            flow_started_count(Flow.ACTIVATION_KEY_CREATE)

        events = await super().run(dispatcher, tracker, domain)
        requested_slot = tracker.get_slot("requested_slot")

        name = tracker.get_slot(ACTIVATION_KEY_NAME)
        if requested_slot == ACTIVATION_KEY_NAME:
            # post to rhsm 	/api/rhsm/v2/activation_keys
            body = {"name": name, "role": "", "serviceLevel": "", "usage": ""}
            response = await send_console_request(
                "rhsm", "/api/rhsm/v2/activation_keys", tracker, method="post", json=body, fetch_content=False
            )

            if response is None or response.status_code != 200: 
                # error json format: {"error":{"code":400,"message":"name should be present, unique and only contain letters, numbers, underscores, or hyphens"}}
                error_message = response.json().get("error", {}).get("message", "")
                dispatcher.utter_message(response="utter_inventory_create_activation_key_failure_1")
                dispatcher.utter_message(response="utter_inventory_create_activation_key_failure_2", error_message=error_message)
            else:
                dispatcher.utter_message(response="utter_inventory_activation_key_create_success")
                flow_finished_count(Flow.ACTIVATION_KEY_CREATE)

        return events

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Text]:
        return domain_slots
