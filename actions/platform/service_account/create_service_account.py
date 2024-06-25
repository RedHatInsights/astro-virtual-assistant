from typing import Any, Text, Dict, List
import re

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, ActiveLoop
from rasa_sdk.types import DomainDict

from common import logging
from common.config import app
from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match

logger = logging.initialize_logging()

NEW_OR_EXISTING = "service_account_new_or_existing"
SERVICE_ACCOUNT_NAME = "service_account_name"
SERVICE_ACCOUNT_DESCRIPTION = "service_account_description"
CREATE_ANOTHER_SERVICE_ACCOUNT = "create_another_service_account"

new_or_existing_choice = FuzzySlotMatch(
    "service_account_new_or_existing",
    [
        FuzzySlotMatchOption("new"),
        FuzzySlotMatchOption("existing"),
    ],
)


class CreateServiceAccount(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_create_service_account"

    async def extract_service_account_new_or_existing(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == NEW_OR_EXISTING:
            resolved = resolve_slot_match(
                tracker.latest_message["text"], new_or_existing_choice, accepted_rate=95
            )

            if len(resolved) > 0:
                return resolved

            return {NEW_OR_EXISTING: None}

        return {}

    async def validate_service_account_new_or_existing(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {NEW_OR_EXISTING: value}

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        requested_slot = tracker.get_slot("requested_slot")

        if (
            requested_slot == NEW_OR_EXISTING
            and tracker.get_slot(NEW_OR_EXISTING) == "existing"
        ):
            dispatcher.utter_message(response="utter_service_account_page_redirect")
            return [
                SlotSet(SERVICE_ACCOUNT_NAME, "set"),
                SlotSet(SERVICE_ACCOUNT_DESCRIPTION, "set"),
            ]

        if requested_slot == SERVICE_ACCOUNT_NAME:
            slot_value = tracker.get_slot(SERVICE_ACCOUNT_NAME)
            if tracker.get_slot(SERVICE_ACCOUNT_NAME):
                pattern = r"^[a-z0-9][a-z0-9\-]*[a-z0-9]$"
                valid = bool(re.match(pattern, slot_value))
                if not valid:
                    dispatcher.utter_message(
                        response="utter_service_account_name_validation_issue"
                    )
                    return [SlotSet(SERVICE_ACCOUNT_NAME, None)]

        if requested_slot == SERVICE_ACCOUNT_DESCRIPTION:
            service_account_name = tracker.get_slot(SERVICE_ACCOUNT_NAME)
            service_account_description = tracker.get_slot(SERVICE_ACCOUNT_DESCRIPTION)
            if service_account_description and len(service_account_description) <= 0:
                dispatcher.utter_message(
                    response="utter_service_account_description_validation_issue"
                )
                return [SlotSet(SERVICE_ACCOUNT_DESCRIPTION, None)]

            if tracker.get_slot(SERVICE_ACCOUNT_NAME) and tracker.get_slot(
                SERVICE_ACCOUNT_DESCRIPTION
            ):
                dispatcher.utter_message(
                    response="utter_dispatch_service_account_create",
                    name=service_account_name,
                    description=service_account_description,
                    environment=app.environment_name,
                )

        if (
            requested_slot == CREATE_ANOTHER_SERVICE_ACCOUNT
            and tracker.get_slot(CREATE_ANOTHER_SERVICE_ACCOUNT) == True
        ):
            return [
                SlotSet(SERVICE_ACCOUNT_NAME, None),
                SlotSet(SERVICE_ACCOUNT_DESCRIPTION, None),
                SlotSet(CREATE_ANOTHER_SERVICE_ACCOUNT, None),
            ]

        return []
