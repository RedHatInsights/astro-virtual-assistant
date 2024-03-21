from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    ActionExecuted,
    SlotSet,
    UserUtteranceReverted,
    ActionReverted,
)
from rasa_sdk.types import DomainDict

from rapidfuzz import fuzz

from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match

from common import logging
from common.header import Header
from common.requests import send_console_request


logger = logging.initialize_logging()

# Slots
_SLOT_IS_ORG_ADMIN = "is_org_admin"
NOTIF_SERVICE = "notifications_service"
NOTIF_SERVICE_OPT = "notifications_service_option"
NOTIF_EVENT = "notifications_event"
NOTIF_EVENT_OPT = "notifications_event_option"
NOTIF_BEHAVIOR_OPT = "notifications_behavior_option"

service_match = FuzzySlotMatch(
    NOTIF_SERVICE,
    [
        FuzzySlotMatchOption("Openshift", ["openshift", "open shift"]),
        FuzzySlotMatchOption("RHEL", ["rhel", "red hat enterprise linux", "linux"]),
        FuzzySlotMatchOption("Core Console", ["core console", "console", "hcc", "platform"]),
        FuzzySlotMatchOption("unsure", ["not sure", "unsure", "idk", "I'm not sure", "no clue", "I have no idea"]),
    ],
)

# going to continue to test phrases
service_opt_match = FuzzySlotMatch(
    NOTIF_SERVICE_OPT,
    [
        FuzzySlotMatchOption("manage events", ["Manage my organization's event settings", "event settings", "org events"]),
        FuzzySlotMatchOption("manage preferences", ["manage my own notification preferences", "manage preferences for my current notifications", "preferences", "pref"]),
        FuzzySlotMatchOption("contact admin", ["contact my org admin for me", "contact my organization's admin", "org admin", "admin"]),
        FuzzySlotMatchOption("learn", ["learn more about notifications", "learn", "help", "docs", "documentation", "learn more", "learn about notifications", "learn about"]),
    ],
)

event_opt_match = FuzzySlotMatch(
    NOTIF_EVENT_OPT,
    [
        FuzzySlotMatchOption("new", ["set up a new event", "add", "new event", "new"]),
        FuzzySlotMatchOption("modify", ["modify settings for an event notification", "edit", "change", "modify", "existing"]),
        FuzzySlotMatchOption("disable", ["disable an event notification", "disable notification please", "delete event", "remove", "delete", "disable"]),
    ],
)

behavior_opt_match = FuzzySlotMatch(
    NOTIF_BEHAVIOR_OPT,
    [
        FuzzySlotMatchOption("attach", ["attach an existing behavior group", "attach", "existing"]),
        FuzzySlotMatchOption("create", ["create a new behavior group", "create", "new", "new behavior"]),
        FuzzySlotMatchOption("remove", ["remove an existing behavior group", "remove", "delete"]),
    ],
)

class ValidateFormNotifications(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_notifications"

    @staticmethod
    def extract_notifications_service(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") != NOTIF_SERVICE:
            return {}

        resolved = resolve_slot_match(
            tracker.latest_message["text"], service_match
        )
        if len(resolved) > 0:
            return resolved
        
        return {}
    
    @staticmethod
    def extract_notifications_service_option(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") != NOTIF_SERVICE_OPT:
            return {}

        resolved = resolve_slot_match(
            tracker.latest_message["text"], service_opt_match
        )
        if len(resolved) > 0:
            return resolved
        
        return {}
    
    @staticmethod
    def extract_notifications_event_option(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") != NOTIF_EVENT_OPT:
            return {}

        resolved = resolve_slot_match(
            tracker.latest_message["text"], event_opt_match
        )
        if len(resolved) > 0:
            return resolved
        
        return {}

    @staticmethod
    def extract_notifications_event(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") != NOTIF_EVENT:
            return {}

        if tracker.latest_message["text"]:
            return {NOTIF_EVENT: tracker.latest_message["text"]}
        
        return {}
    
    @staticmethod
    def extract_notifications_behavior_option(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") != NOTIF_BEHAVIOR_OPT:
            return {}

        resolved = resolve_slot_match(
            tracker.latest_message["text"], behavior_opt_match
        )
        if len(resolved) > 0:
            return resolved
        
        return {}

    @staticmethod
    def validate_notifications_service(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {NOTIF_SERVICE: value}
    
    @staticmethod
    def validate_notifications_service_opt(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {NOTIF_SERVICE_OPT: value}
    
    @staticmethod
    def validate_notifications_event_opt(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {NOTIF_EVENT_OPT: value}
    
    @staticmethod
    def validate_notifications_event(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {NOTIF_EVENT: value}
    
    @staticmethod
    def validate_notifications_behavior_opt(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {NOTIF_BEHAVIOR_OPT: value}

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        events = await super().run(dispatcher, tracker, domain)
        requested_slot = tracker.get_slot("requested_slot")

        if requested_slot == NOTIF_SERVICE_OPT:
            option = tracker.get_slot(NOTIF_SERVICE_OPT)
            if option == "manage events":
                dispatcher.utter_message(response="utter_notifications_edit")
                dispatcher.utter_message(response="utter_notifications_manage_events_which_service")
            elif option == "manage preferences":
                # services = await get_available_services(tracker) + ["Other"]
                services = ["Openshift", "RHEL", "Core Console", "Other"]
                dispatcher.utter_message(response="utter_notifications_edit_non_admin", buttons=services)
            elif option == "contact admin":
                events.append(SlotSet("requested_slot", None))
            elif option == "learn":
                dispatcher.utter_message(response="utter_notifications_learn")
                dispatcher.utter_message(response="utter_notifications_learn_dashboard")
                dispatcher.utter_message(response="utter_notifications_learn_docs")
                events.append(SlotSet("requested_slot", None))
        
        if requested_slot == NOTIF_SERVICE:
            service = tracker.get_slot(NOTIF_SERVICE)
            option = tracker.get_slot(NOTIF_SERVICE_OPT)
            if service == "unsure":
                dispatcher.utter_message(response="utter_notifications_learn")
                dispatcher.utter_message(response="utter_notifications_learn_dashboard")
                dispatcher.utter_message(response="utter_notifications_learn_docs")
                events.append(SlotSet("requested_slot", None))
            else:
                # events = await get_available_events_for_service(tracker, service)
                dispatcher.utter_message(response="utter_notifications_setup_for_chosen_service", service=service)
                dispatcher.utter_message(response="utter_notifications_edit_events_for_service", service=service, buttons=["Event type | Service", "Event type | Service", "Event type | Service"])

        if requested_slot == NOTIF_EVENT_OPT:
            option = tracker.get_slot(NOTIF_EVENT_OPT)
            if option == "set up":
                dispatcher.utter_message(response="utter_notifications_setup_which_service")
                events.append(SlotSet("requested_slot", NOTIF_SERVICE))
                events.append(SlotSet(NOTIF_SERVICE_OPT, "manage events"))
            elif option == "modify":
                dispatcher.utter_message(response="utter_notifications_edit_events_which_service")
            elif option == "disable":
                dispatcher.utter_message(response="utter_notifications_disable_event")
                dispatcher.utter_message(response="utter_notifications_disable_event_which_service")
        
        if requested_slot == NOTIF_EVENT:
            service = tracker.get_slot(NOTIF_SERVICE)
            event = tracker.get_slot(NOTIF_EVENT)
            # events = await get_available_events_for_service(tracker, service)
            dispatcher.utter_message(response="utter_notifications_edit_selected_event", event=event)
        
        return events

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Text]:
        return domain_slots


class ActionNotificationsReset(Action):
    def name(self) -> Text:
        return "action_notifications_reset"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        return [SlotSet(NOTIF_SERVICE, None), SlotSet(NOTIF_SERVICE_OPT, None), SlotSet(NOTIF_EVENT, None), SlotSet(NOTIF_EVENT_OPT, None)]


class ActionNotificationsSetup(Action):
    def name(self) -> Text:
        return "action_notifications_setup"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        is_org_admin = tracker.get_slot(_SLOT_IS_ORG_ADMIN)
        if is_org_admin is False:
            dispatcher.utter_message(response="utter_notifications_non_admin")
            dispatcher.utter_message(response="utter_notifications_setup_non_admin_can_help")
            return [SlotSet("requested_slot", NOTIF_SERVICE_OPT)]
        else:
            dispatcher.utter_message(response="utter_notifications_setup")
            dispatcher.utter_message(response="utter_notifications_setup_which_service")
            return [SlotSet("requested_slot", NOTIF_SERVICE), SlotSet(NOTIF_SERVICE_OPT, "new")]


async def get_available_services(tracker: Tracker) -> List[str]:
    pass


async def get_available_events_for_service(tracker: Tracker, service: str) -> List[str]:
    pass
