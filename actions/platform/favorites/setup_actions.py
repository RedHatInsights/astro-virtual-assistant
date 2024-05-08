from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match
from actions.platform.chrome import create_service_options
from actions.platform.favorites import (
    _FAVE_SERVICE,
    _FAVE_SUGGESTIONS,
    _FAVE_UNHAPPY,
)


class ActionFavoritesReset(Action):
    def name(self) -> Text:
        return "action_favorites_reset"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        return [
            SlotSet(_FAVE_SERVICE),
            SlotSet(_FAVE_SUGGESTIONS),
            SlotSet(_FAVE_UNHAPPY),
        ]


class ActionFavoritesExtract(Action):
    def name(self) -> Text:
        return "action_favorites_extract"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        intent = tracker.get_intent_of_latest_message()
        specified_favorite = str(
            next(tracker.get_latest_entity_values("core_services"), None)
        )

        if specified_favorite is not None:
            options = await create_service_options(tracker)
            fuzzy_options = [*map(lambda o: FuzzySlotMatchOption(o["data"]["title"], o["synonyms"]), options.values())]
            match = FuzzySlotMatch(_FAVE_SERVICE, fuzzy_options)

            resolved = resolve_slot_match(
                specified_favorite, match
            )
            if len(resolved) > 0:
                return [
                    SlotSet(_FAVE_SERVICE, resolved[_FAVE_SERVICE]),
                    SlotSet("requested_slot", _FAVE_SERVICE),
                ]

        if intent == "intent_favorites_add":
            dispatcher.utter_message(response="utter_favorites_add_start")
            dispatcher.utter_message(response="utter_favorites_add_select")
        if intent == "intent_favorites_delete":
            dispatcher.utter_message(response="utter_favorites_delete_start")
            dispatcher.utter_message(response="utter_favorites_delete_select")
        return []
