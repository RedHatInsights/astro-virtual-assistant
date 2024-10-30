import re
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict

from actions.actions import form_action_is_starting

from common import logging
from common.metrics import (
    flow_started_count,
    Flow,
    flow_finished_count,
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
    def validate_inventory_activation_key_name(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        # must contain only numbers, letters, underscores, and hyphens.
        print("value: ", value)
        pattern = r'^[a-zA-Z0-9_-]+$'
        if value and re.match(pattern, value):
            return {ACTIVATION_KEY_NAME: value}
        dispatcher.utter_message(response="utter_inventory_activation_key_name_invalid")
        return {ACTIVATION_KEY_NAME: None}

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        if await form_action_is_starting(self, dispatcher, tracker, domain):
            flow_started_count(Flow.ACTIVATION_KEY_CREATE)

        events = await super().run(dispatcher, tracker, domain)
        requested_slot = tracker.get_slot("requested_slot")

        name = tracker.get_slot(ACTIVATION_KEY_NAME)
        if requested_slot == ACTIVATION_KEY_NAME and name:
            # post to rhsm 	/api/rhsm/v2/activation_keys
            body = {"name": name, "role": "", "serviceLevel": "", "usage": ""}
            response = await send_console_request(
                "rhsm", "/api/rhsm/v2/activation_keys", tracker, method="post", json=body, fetch_content=False
            )

            if not response.ok: 
                # error json format: {"error":{"code":400,"message":"name should be present, unique and only contain letters, numbers, underscores, or hyphens"}}
                error_json = await response.json()
                error_message = error_json.get("error", {}).get("message", "Unknown error")
                dispatcher.utter_message(response="utter_inventory_create_activation_key_failure_1")
                dispatcher.utter_message(response="utter_inventory_create_activation_key_failure_2", error_message=error_message)
                logger.error(
                    "Failed to get a response from the rhsm API: status {}; result {}".format(
                        response.status, error_message
                    ),
                    exc_info=True,
                )
                flow_finished_count(Flow.ACTIVATION_KEY_CREATE, sub_flow_name="error")
            else:
                dispatcher.utter_message(response="utter_inventory_create_activation_key_success")
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

class ActionActivationKeysClear(Action):
    def name(self) -> Text:
        return "action_inventory_create_activation_key_clear"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        return [
            SlotSet(ACTIVATION_KEY_NAME, None),
        ]
