from typing import List, Dict, Text, Any
from urllib.parse import urlparse

from rasa_sdk import FormValidationAction, Tracker, Action
from rasa_sdk.events import SlotSet, EventType, ActiveLoop
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match
from actions.platform.chrome import create_service_options, add_service_to_favorites
from common.requests import send_console_request

_FAVE_SERVICE = "favorites_service"
_FAVE_OPTIONS = "favorites_options"

class AddFavoritesForm(FormValidationAction):
    def name(self) -> str:
        return "validate_form_favorites_add"
    
    async def extract_favorites_service(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if tracker.get_slot("requested_slot") != _FAVE_SERVICE:
            return {}
        
        message = tracker.latest_message.get("text")
        return { _FAVE_SERVICE: message}
    
    @staticmethod
    async def validate_favorites_service(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if value == "unsure":
            return {_FAVE_SERVICE: value}
        if value == None:
            print("Value is None")
            return {_FAVE_SERVICE: None}
        
        options = await create_service_options(tracker)
        match = FuzzySlotMatch(_FAVE_SERVICE, options)

        print("Matching service options")
        print(options)

        resolved = resolve_slot_match(
            value,
            match
        )
        if len(resolved) > 0:
            return resolved

        return {_FAVE_SERVICE: None}

    async def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[EventType]:
        events = await super().run(dispatcher, tracker, domain)
        requested_slot = tracker.get_slot("requested_slot")

        if requested_slot == _FAVE_SERVICE:
            service = tracker.get_slot(_FAVE_SERVICE)
            if service == "unsure":
                dispatcher.utter_message(response="utter_favorites_how")
            if service == None:
                print("Service is None")
            else:
                dispatcher.utter_message(response="utter_favorites_add_specified", service=service["title"])
                result = await add_service_to_favorites(tracker, service)
                if result.ok:
                    print("Service added to favorites")
                    dispatcher.utter_message(response="utter_favorites_add_success", service=service["title"])
                else:
                    print("Failed to add service to error")
                    dispatcher.utter_message(response="utter_favorites_add_failed", service=service["title"])
        return events
    
    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Text]:
        return domain_slots
