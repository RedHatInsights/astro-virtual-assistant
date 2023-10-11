from typing import Text, Dict, List, Any

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action
from rasa_sdk.events import SlotSet, UserUtteranceReverted


class ActionBack(Action):
    """Revert the tracker state by one user utterances."""

    def name(self) -> Text:
        return "action_core_one_back"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        return [UserUtteranceReverted()]


class ActionFirstSessionStart(Action):
    """Fired after `intent_core_session_start` the first time the session starts"""

    def name(self) -> Text:
        return "action_core_first_session_start"

    async def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        return [SlotSet("first_time_greeting", False)]
