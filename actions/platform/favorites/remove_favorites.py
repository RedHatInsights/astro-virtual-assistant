from typing import List, Dict, Text, Any
from urllib.parse import urlparse

from rasa_sdk import FormValidationAction, Tracker, Action
from rasa_sdk.events import SlotSet, EventType, ActiveLoop
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match
from common.requests import send_console_request


class RemoveFavoritesForm(FormValidationAction):
    def name(self) -> str:
        return "validate_form_favorites_remove"

    async def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[EventType]:
        events = await super().run(dispatcher, tracker, domain)
        requested_slot = tracker.get_slot("requested_slot")

        # if requested_slot == _FAVE_SERVICE:
        #     option = tracker.get_slot(_FAVE_SERVICE)
        #     if option == "manage events":

        return events
    
    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Text]:
        updated_slots = domain_slots.copy()

        return updated_slots
