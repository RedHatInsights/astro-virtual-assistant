from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, ActiveLoop
from rasa_sdk.types import DomainDict

from common import logging
from common.config import app
from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match

logger = logging.initialize_logging()

DOCS_OR_ACCOUNT_SLOT = "docs_or_walkthrough"
HAS_SERVICE_ACC_CREDS = "has_service_account_creds"
NEED_ANOTHER_INTEGRATION = "need_another_integration"

docs_or_account_choice = FuzzySlotMatch(
    "docs_or_walkthrough",
    [
        FuzzySlotMatchOption("docs", ["docs", "documentation", "doc"]),
        FuzzySlotMatchOption(
            "walkthrough",
            ["walkthrough", "walk"],
        ),
    ],
)


class UpdateApiIntegration(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_update_api_integration"

    @staticmethod
    def extract_docs_or_walkthrough(
        dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == DOCS_OR_ACCOUNT_SLOT:
            resolved = resolve_slot_match(
                tracker.latest_message["text"], docs_or_account_choice, accepted_rate=95
            )

            if len(resolved) > 0:
                return resolved

            return {DOCS_OR_ACCOUNT_SLOT: None}

        return {}

    @staticmethod
    def validate_docs_or_walkthrough(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {DOCS_OR_ACCOUNT_SLOT: value}

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        requested_slot = tracker.get_slot("requested_slot")

        if tracker.get_slot(DOCS_OR_ACCOUNT_SLOT) == "docs":
            dispatcher.utter_message(response="utter_docs_only_redirect")
            return [
                SlotSet(HAS_SERVICE_ACC_CREDS, False),
                SlotSet(NEED_ANOTHER_INTEGRATION, False),
            ]

        if tracker.get_slot(DOCS_OR_ACCOUNT_SLOT) == "walkthrough":
            if requested_slot == HAS_SERVICE_ACC_CREDS:
                if tracker.get_slot(HAS_SERVICE_ACC_CREDS) == True:
                    dispatcher.utter_message(
                        response="utter_got_service_account_creds_1"
                    )
                    dispatcher.utter_message(
                        response="utter_got_service_account_creds_2"
                    )
                    dispatcher.utter_message(
                        response="utter_got_service_account_creds_3"
                    )
                    dispatcher.utter_message(
                        response="utter_got_service_account_creds_4"
                    )
                    dispatcher.utter_message(
                        response="utter_got_service_account_creds_5"
                    )
                    dispatcher.utter_message(
                        response="utter_got_service_account_creds_6",
                        access_token="{ACCESS_TOKEN}",
                    )
                    dispatcher.utter_message(
                        response="utter_got_service_account_creds_7",
                        access_token="{ACCESS_TOKEN}",
                    )
                    dispatcher.utter_message(
                        response="utter_got_service_account_creds_8"
                    )

                if tracker.get_slot(HAS_SERVICE_ACC_CREDS) == False:
                    dispatcher.utter_message(response="utter_no_service_account_creds")

        return []


class ActionFormUpdateApiIntegrationCheck(Action):
    def name(self) -> Text:
        return "action_form_update_api_integration_check"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:

        docs_or_account = tracker.get_slot(DOCS_OR_ACCOUNT_SLOT)
        need_another_integration = tracker.get_slot(NEED_ANOTHER_INTEGRATION)

        if docs_or_account == "walkthrough":
            if need_another_integration:
                return [
                    SlotSet(DOCS_OR_ACCOUNT_SLOT, "walkthrough"),
                    SlotSet(HAS_SERVICE_ACC_CREDS, None),
                    SlotSet(NEED_ANOTHER_INTEGRATION, None),
                    ActiveLoop("form_update_api_integration"),
                ]

        return [
            SlotSet(DOCS_OR_ACCOUNT_SLOT, None),
            SlotSet(HAS_SERVICE_ACC_CREDS, None),
            SlotSet(NEED_ANOTHER_INTEGRATION, None),
            ActiveLoop("form_closing"),
        ]
