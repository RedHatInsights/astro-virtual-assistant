from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict

from actions.slot_match import resolve_slot_match
from actions.platform.notifications import (
    _SLOT_IS_ORG_ADMIN,
    NOTIF_BUNDLE_OPT,
    NOTIF_TROUBLESHOOT_TO_INTEGRATIONS,
    NOTIF_TROUBLESHOOT_TO_NOTIFICATIONS,
    service_opt_match,
)


class ValidateFormNotificationsTroubleshoot(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_notifications_troubleshoot"

    @staticmethod
    def extract_notifications_bundle_option(
        dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if (
            tracker.get_slot("requested_slot") != NOTIF_BUNDLE_OPT
            or tracker.get_slot(NOTIF_BUNDLE_OPT) == "learn"
        ):
            return {}

        resolved = resolve_slot_match(tracker.latest_message["text"], service_opt_match)
        if len(resolved) > 0:
            return resolved

        return {"requested_slot": None}

    @staticmethod
    def validate_notifications_bundle_option(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {NOTIF_BUNDLE_OPT: value}

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        events = await super().run(dispatcher, tracker, domain)
        requested_slot = tracker.get_slot("requested_slot")

        if requested_slot == NOTIF_BUNDLE_OPT:
            option = tracker.get_slot(NOTIF_BUNDLE_OPT)
            if option == "manage events":
                dispatcher.utter_message(response="utter_notifications_edit_events_how")
                events.append(SlotSet(NOTIF_TROUBLESHOOT_TO_NOTIFICATIONS, True))
            elif option == "manage preferences":
                dispatcher.utter_message(response="utter_notifications_edit_non_admin")
                events.append(SlotSet(NOTIF_TROUBLESHOOT_TO_NOTIFICATIONS, True))
            elif option == "manage integrations":
                events.append(SlotSet(NOTIF_TROUBLESHOOT_TO_INTEGRATIONS, True))
            elif option == "learn":
                dispatcher.utter_message(response="utter_notifications_learn")
                dispatcher.utter_message(response="utter_notifications_learn_dashboard")
                dispatcher.utter_message(response="utter_notifications_learn_docs")

        return events

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Text]:
        return domain_slots


class ActionNotificationsTroubleshoot(Action):
    def name(self) -> Text:
        return "action_notifications_troubleshoot"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        is_org_admin = tracker.get_slot(_SLOT_IS_ORG_ADMIN)

        if is_org_admin:
            dispatcher.utter_message(
                response="utter_notifications_troubleshoot_org_admin"
            )
        else:
            dispatcher.utter_message(
                response="utter_notifications_troubleshoot_non_admin"
            )

        return []
