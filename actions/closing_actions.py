from typing import Text, Dict, List, Any

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action
from rasa_sdk.events import SlotSet


class ActionGotHelp(Action):
    def name(self) -> Text:
        return "action_closing_got_help"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        last_intent = tracker.get_intent_of_latest_message(True)
        if last_intent == "intent_core_yes":
            return [SlotSet("closing_got_help", True)]
        elif last_intent == "intent_core_no":
            return [SlotSet("closing_got_help", False)]

        return []


class ActionShareFeedback(Action):
    def name(self) -> Text:
        return "action_closing_share_feedback"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        # Todo: Insert logic to send feedback to the platform
        return [SlotSet("closing_feedback", None)]
