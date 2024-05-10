from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    ActionExecuted,
    SlotSet,
)
from rasa_sdk.types import DomainDict

from common import logging
from common.config import app
from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match

logger = logging.initialize_logging()

_SLOT_IS_ORG_ADMIN = "is_org_admin"

ORG_OR_ACCOUNT_SLOT = "org_or_account"
PERSONAL_2FA_REDIRECT_CONFIRM = "personal_2fa_redirect_confirm"
ORG_2FA_ENABLE_CONFIRM = "org_2fa_enable_confirm"

org_or_account_choice = FuzzySlotMatch(
    "org_or_account",
    [
        FuzzySlotMatchOption("org", ["org", "organization", "everyone", "all user", "all accounts"]),
        FuzzySlotMatchOption(
            "personal", ["personal", "my own", "individual", "single", "my account", "just me", "just for me"]
        ),
    ],
)

class ActionAskFormEnable2faOrgOrAccount(Action):
    def name(self) -> Text:
        return "action_ask_form_enable_2fa_org_or_account"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        is_org_admin = tracker.get_slot(_SLOT_IS_ORG_ADMIN)
        results = []

        if is_org_admin:
            dispatcher.utter_message(response="utter_user_is_org_admin")

        return results


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

        if requested_slot == ORG_OR_ACCOUNT_SLOT:
            option = tracker.get_slot(ORG_OR_ACCOUNT_SLOT)

            if not is_org_admin:
                option = "personal"

            if option == "personal":
                dispatcher.utter_message(response="utter_enable_2fa_individual_1")
                dispatcher.utter_message(response="utter_enable_2fa_individual_2")
            elif option == "org" and is_org_admin:
                dispatcher.utter_message(response="utter_enable_org_2fa_info_1")
                dispatcher.utter_message(response="utter_enable_org_2fa_info_2")

        return []

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Text]:
        updated_slots = domain_slots.copy()

        if tracker.get_slot(ORG_OR_ACCOUNT_SLOT) == "org":
            updated_slots.remove("personal_2fa_redirect_confirm")

        if tracker.get_slot(ORG_OR_ACCOUNT_SLOT) == "personal":
            updated_slots.remove("org_2fa_enable_confirm")

        return updated_slots


class ActionEnableOrg2FaCommand(Action):
    def name(self) -> Text:
        return "action_enable_2fa"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        org_or_account_2fa = tracker.get_slot(ORG_OR_ACCOUNT_SLOT)
        personal_2fa_redirect = tracker.get_slot(PERSONAL_2FA_REDIRECT_CONFIRM)
        enable_org_2fa = tracker.get_slot(ORG_2FA_ENABLE_CONFIRM)

        if org_or_account_2fa == "org" and enable_org_2fa:
            dispatcher.utter_message(
                response="utter_manage_org_2fa_command",
                enable_org_2fa="true",
                environment=app.environment_name,
            )
            dispatcher.utter_message(response="utter_enable_org_2fa_success_1")
            dispatcher.utter_message(response="utter_enable_org_2fa_success_2")
        if org_or_account_2fa == "personal" and personal_2fa_redirect:
            dispatcher.utter_message(response="utter_individual_2fa_form_redirect")

        return [
            SlotSet(ORG_OR_ACCOUNT_SLOT, None),
            SlotSet(PERSONAL_2FA_REDIRECT_CONFIRM, None),
            SlotSet(ORG_2FA_ENABLE_CONFIRM, None)
        ]
