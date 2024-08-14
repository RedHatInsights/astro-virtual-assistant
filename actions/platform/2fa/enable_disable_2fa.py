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

ORG_OR_ACCOUNT_ENABLE_SLOT = "org_or_account_2fa_enable"
ORG_OR_ACCOUNT_DISABLE_SLOT = "org_or_account_2fa_disable"
ENABLE_2FA_FORM_CONTINUE = "enable_2fa_continue"
DISABLE_2FA_FORM_CONTINUE = "disable_2fa_continue"

org_account_options = [
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
]


org_or_account_enable_choice = FuzzySlotMatch(
    "org_or_account_2fa_enable", org_account_options
)

org_or_account_disable_choice = FuzzySlotMatch(
    "org_or_account_2fa_disable", org_account_options
)


class ActionEnableDisable2faFormPrefill(Action):
    def name(self) -> Text:
        return "action_enable_disable_2fa_form_prefill"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        is_org_admin = tracker.get_slot(_SLOT_IS_ORG_ADMIN)

        if is_org_admin:
            return []

        return [SlotSet(ORG_OR_ACCOUNT_ENABLE_SLOT, "personal"), SlotSet(ORG_OR_ACCOUNT_DISABLE_SLOT, "personal")]


class Enable2fa(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_enable_2fa"

    async def extract_org_or_account_2fa_enable(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        requested_slot = tracker.get_slot("requested_slot")
        user_message = tracker.latest_message["text"]

        if requested_slot == ORG_OR_ACCOUNT_ENABLE_SLOT:
            resolved = self.resolve_org_or_account(user_message)

            if len(resolved) > 0:
                logger.info(f"resolved... {resolved}")
                return resolved

        if (
            requested_slot is None
            and tracker.get_slot(ORG_OR_ACCOUNT_ENABLE_SLOT) is None
        ):
            resolved = self.resolve_org_or_account(user_message)

            if len(resolved) > 0:
                logger.info(f"resolved2... {resolved}")
                return resolved

        return {}

    async def validate_org_or_account_2fa_enable(
        self,
        value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        logger.info("validate...", value)
        return {ORG_OR_ACCOUNT_ENABLE_SLOT: value}

    def resolve_org_or_account(self, user_input):
        for word in user_input.split(" "):
            resolved = resolve_slot_match(word, org_or_account_enable_choice)
            if len(resolved) > 0:
                return resolved

        return {}

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        is_org_admin = tracker.get_slot(_SLOT_IS_ORG_ADMIN)
        requested_slot = tracker.get_slot("requested_slot")
        logger.info(f"testing... {tracker.get_slot(ORG_OR_ACCOUNT_ENABLE_SLOT)} {tracker.get_slot('requested_slot')}")

        if (
            requested_slot == None
            and tracker.get_slot(ORG_OR_ACCOUNT_ENABLE_SLOT) == "personal"
        ):
            dispatcher.utter_message(response="utter_enable_2fa_individual_1")
            dispatcher.utter_message(response="utter_enable_2fa_individual_2")
            return

        if requested_slot == ORG_OR_ACCOUNT_ENABLE_SLOT:
            option = tracker.get_slot(ORG_OR_ACCOUNT_ENABLE_SLOT)
            if option == "personal":
                dispatcher.utter_message(response="utter_enable_2fa_individual_1")
                dispatcher.utter_message(response="utter_enable_2fa_individual_2")
            elif option == "org" and is_org_admin:
                dispatcher.utter_message(response="utter_enable_org_2fa_info_1")
                dispatcher.utter_message(response="utter_enable_org_2fa_info_2")

        return []


class ActionEnable2fa(Action):
    def name(self) -> Text:
        return "action_enable_2fa"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        org_or_account_2fa = tracker.get_slot(ORG_OR_ACCOUNT_ENABLE_SLOT)
        enable_2fa_continue = tracker.get_slot(ENABLE_2FA_FORM_CONTINUE)

        if enable_2fa_continue:
            if org_or_account_2fa == "org":
                dispatcher.utter_message(
                    response="utter_manage_org_2fa_command",
                    enable_org_2fa="true",
                    environment=app.environment_name,
                )
            if org_or_account_2fa == "personal":
                dispatcher.utter_message(response="utter_individual_2fa_form_redirect")

        return [
            SlotSet(ORG_OR_ACCOUNT_ENABLE_SLOT, None),
            SlotSet(ORG_OR_ACCOUNT_DISABLE_SLOT, None),
            SlotSet(ENABLE_2FA_FORM_CONTINUE, None),
        ]


class FormDisable2fa(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_disable_2fa"

    async def extract_org_or_account_2fa_disable(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") == ORG_OR_ACCOUNT_DISABLE_SLOT:
            resolved = resolve_slot_match(
                tracker.latest_message["text"], org_or_account_disable_choice, accepted_rate=95
            )

            if len(resolved) > 0:
                return resolved

            return {ORG_OR_ACCOUNT_DISABLE_SLOT: None}

        return {}

    async def validate_org_or_account_2fa_disable(
        self,
        value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {ORG_OR_ACCOUNT_DISABLE_SLOT: value}

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        is_org_admin = tracker.get_slot(_SLOT_IS_ORG_ADMIN)
        requested_slot = tracker.get_slot("requested_slot")

        if (
            requested_slot == None
            and tracker.get_slot(ORG_OR_ACCOUNT_DISABLE_SLOT) == "personal"
        ):
            dispatcher.utter_message(response="utter_disable_2fa_individual_1")
            dispatcher.utter_message(response="utter_disable_2fa_individual_2")
            return

        if requested_slot == ORG_OR_ACCOUNT_DISABLE_SLOT:
            option = tracker.get_slot(ORG_OR_ACCOUNT_DISABLE_SLOT)
            if option == "personal":
                dispatcher.utter_message(response="utter_disable_2fa_individual_1")
                dispatcher.utter_message(response="utter_disable_2fa_individual_2")
            elif option == "org" and is_org_admin:
                dispatcher.utter_message(response="utter_disable_org_2fa_info")

        return []


class ActionDisable2fa(Action):
    def name(self) -> Text:
        return "action_disable_2fa"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        org_or_account_2fa = tracker.get_slot(ORG_OR_ACCOUNT_DISABLE_SLOT)
        enable_2fa_continue = tracker.get_slot(DISABLE_2FA_FORM_CONTINUE)

        if enable_2fa_continue:
            if org_or_account_2fa == "org":
                dispatcher.utter_message(
                    response="utter_manage_org_2fa_command",
                    enable_org_2fa="false",
                    environment=app.environment_name,
                )
            if org_or_account_2fa == "personal":
                dispatcher.utter_message(response="utter_individual_2fa_form_redirect")

        return [
            SlotSet(ORG_OR_ACCOUNT_DISABLE_SLOT, None),
            SlotSet(ORG_OR_ACCOUNT_ENABLE_SLOT, None),
            SlotSet(DISABLE_2FA_FORM_CONTINUE, None),
        ]
