from typing import Dict, Text, Any

from rasa_sdk import FormValidationAction, Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions.slot_match import (
    FuzzySlotMatch,
    FuzzySlotMatchOption,
    resolve_slot_match,
    suggest_using_slot_match,
)
from actions.platform.chrome import (
    create_service_options,
)

_FAVE_SERVICE = "favorites_service"
_FAVE_UNHAPPY = "favorites_unhappy"
_FAVE_SUGGESTIONS = "favorites_suggestions"


class AbstractFavoritesForm(FormValidationAction):
    def name(self) -> str:
        return ""

    async def extract_favorites_service(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict
    ) -> Dict[Text, Any]:
        if (
            tracker.get_slot("requested_slot") != _FAVE_SERVICE
            or tracker.get_slot(_FAVE_SERVICE) != None
        ):
            return {}

        message = tracker.latest_message.get("text")
        options = await create_service_options(tracker)
        fuzzy_options = [
            *map(
                lambda o: FuzzySlotMatchOption(o["data"]["title"], o["synonyms"]),
                options.values(),
            )
        ]
        match = FuzzySlotMatch(_FAVE_SERVICE, fuzzy_options)
        resolved = resolve_slot_match(message, match)

        if len(resolved) > 0:
            return {_FAVE_SERVICE: options[resolved[_FAVE_SERVICE]]["data"]}

        suggestions = suggest_using_slot_match(message, match, accepted_rate=10)

        if suggestions:
            if len(suggestions) > 0:
                suggestions = suggestions[:3]

            return {
                _FAVE_SUGGESTIONS: [
                    *map(lambda s: options[s["value"]]["data"], suggestions)
                ]
            }

        return None

    @staticmethod
    def validate_favorites_service(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if value == None or isinstance(value, dict):
            return {_FAVE_SERVICE: value}

        return {}

    def create_suggestion_buttons(
        self,
        tracker: Tracker,
    ):
        suggestions = tracker.get_slot(_FAVE_SUGGESTIONS)
        buttons = []
        if suggestions:
            for suggestion in suggestions:
                buttons.append(
                    {
                        "title": f'{suggestion["title"]} ({suggestion["group"]})',
                        "payload": suggestion["href"],
                    }
                )

        return buttons
