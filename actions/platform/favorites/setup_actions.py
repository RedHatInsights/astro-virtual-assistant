from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match
from actions.platform.chrome import get_user_favorites


class ActionFavoritesReset(Action):
    def name(self) -> Text:
        return "action_favorites_reset"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        return [
            SlotSet("favorites_service"),
            SlotSet("favorites_options"),
        ]

class ActionFavoritesExtract(Action):
    def name(self) -> Text:
        return "action_favorites_extract"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        specified_favorite = tracker.get_latest_entity_values("core_services")
        print(specified_favorite)
        # favorites = await get_user_info(tracker)
        # if user_info is None or "data" not in user_info or "":
        #     return []
        # entities = tracker.latest_message.get("entities", [])
        # for e in entities:
        #     pass
