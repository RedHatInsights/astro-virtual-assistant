from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from actions.platform.tam import _TAM_SLOTS


class ActionAccessRequestTAMReset(Action):
    def name(self) -> Text:
        return "action_access_request_tam_reset"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        print("Resetting TAM slots")
        return [SlotSet(slot, None) for slot in _TAM_SLOTS]
