from typing import Text, Dict, List, Any

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action
from rasa_sdk.events import ActionExecuted, EventType, SessionStarted, SlotSet

SLOTS_TO_PERSIST = ['first_time_greeting']
SLOT_DEFAULTS = {
    "first_time_greeting": True
}


class ActionSessionStarted(Action):
    def name(self) -> Text:
        return "action_session_start"

    @staticmethod
    def fetch_slots(tracker: Tracker) -> List[EventType]:
        slots = []
        for slot_name in SLOTS_TO_PERSIST:
            value = tracker.get_slot(slot_name)
            if value is None and slot_name in SLOT_DEFAULTS:
                value = SLOT_DEFAULTS.get(slot_name)

            if value is not None:
                slots.append(SlotSet(key=slot_name, value=value))
        return slots

    async def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        return [
            SessionStarted(),
            *self.fetch_slots(tracker),
            ActionExecuted("action_listen")
        ]
