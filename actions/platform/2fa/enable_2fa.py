from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    SlotSet,
)
from rasa_sdk.types import DomainDict

from common import logging
from common.config import app
from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match

logger = logging.initialize_logging()

_SLOT_IS_ORG_ADMIN = "is_org_admin"

ORG_OR_ACCOUNT_SLOT = "org_or_account"
ENABLE_2FA_FORM_CONTINUE = "enable_2fa_continue"


org_or_account_choice = FuzzySlotMatch(
    "org_or_account",
    [
        FuzzySlotMatchOption(
            "org", ["org", "organization", "everyone", "all user", "all accounts"]
        ),
        FuzzySlotMatchOption(
            "personal",
            [
                "personal",
                "my own",
                "myself",
                "individual",
                "single",
                "my account",
                "just me",
                "just for me",
            ],
        ),
    ],
)


class ActionAskFormEnable2faOrgOrAccount(Action):
    def name(self) -> Text:
        return "action_enable_2fa_form_prefill"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        is_org_admin = tracker.get_slot(_SLOT_IS_ORG_ADMIN)

        if is_org_admin:
            return

        return [SlotSet(ORG_OR_ACCOUNT_SLOT, "personal")]


class Enable2fa(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_enable_2fa"

    @staticmethod
    def extract_org_or_account(
        dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == ORG_OR_ACCOUNT_SLOT:
            resolved = resolve_slot_match(
                tracker.latest_message["text"], org_or_account_choice, accepted_rate=95
            )

            if len(resolved) > 0:
                return resolved

            return {ORG_OR_ACCOUNT_SLOT: None}

        return {}

    @staticmethod
    def validate_org_or_account(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {ORG_OR_ACCOUNT_SLOT: value}

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        is_org_admin = tracker.get_slot(_SLOT_IS_ORG_ADMIN)
        requested_slot = tracker.get_slot("requested_slot")

        if tracker.get_slot(ORG_OR_ACCOUNT_SLOT) == "personal":
            dispatcher.utter_message(response="utter_enable_2fa_individual_1")
            dispatcher.utter_message(response="utter_enable_2fa_individual_2")
            return

        if requested_slot == ORG_OR_ACCOUNT_SLOT:
            option = tracker.get_slot(ORG_OR_ACCOUNT_SLOT)
            if option == "personal":
                dispatcher.utter_message(response="utter_enable_2fa_individual_1")
                dispatcher.utter_message(response="utter_enable_2fa_individual_2")
            elif option == "org" and is_org_admin:
                dispatcher.utter_message(response="utter_enable_org_2fa_info_1")
                dispatcher.utter_message(response="utter_enable_org_2fa_info_2")

        return []


class ActionEnableOrg2FaCommand(Action):
    def name(self) -> Text:
        return "action_enable_2fa"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        org_or_account_2fa = tracker.get_slot(ORG_OR_ACCOUNT_SLOT)
        enable_2fa_continue = tracker.get_slot(ENABLE_2FA_FORM_CONTINUE)

        if enable_2fa_continue:
            if org_or_account_2fa == "org":
                dispatcher.utter_message(
                    response="utter_manage_org_2fa_command",
                    enable_org_2fa="true",
                    environment=app.environment_name,
                )
                dispatcher.utter_message(response="utter_enable_org_2fa_success_1")
                dispatcher.utter_message(response="utter_enable_org_2fa_success_2")
            if org_or_account_2fa == "personal":
                dispatcher.utter_message(response="utter_individual_2fa_form_redirect")

        return [
            SlotSet(ORG_OR_ACCOUNT_SLOT, None),
            SlotSet(ENABLE_2FA_FORM_CONTINUE, None),
        ]
