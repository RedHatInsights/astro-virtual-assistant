from typing import Dict, Text, Any

from rasa_sdk import FormValidationAction, Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions.slot_match import (
    FuzzySlotMatch,
    resolve_slot_match,
    suggest_using_slot_match,
)
from actions.platform.chrome import (
    create_service_options,
)

_FAVE_SERVICE = "favorites_service"
_FAVE_OPTIONS = "favorites_options"
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
        match = FuzzySlotMatch(_FAVE_SERVICE, options)

        resolved = resolve_slot_match(message, match)
        if len(resolved) > 0:
            return resolved

        suggestions = suggest_using_slot_match(message, match, accepted_rate=10)

        if suggestions and len(suggestions) > 0:
            suggestions = suggestions[:3]

        return {_FAVE_SUGGESTIONS: suggestions}

    @staticmethod
    def validate_favorites_service(
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if value == "unsure" or value == None or isinstance(value, dict):
            return {_FAVE_SERVICE: value}

        return {}
