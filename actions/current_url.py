from typing import Text, Dict, List, Any

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action
from rasa_sdk.events import SlotSet

from .utils import is_user_event

class ActionSetCurrentURL(Action):
    """Sets the user's current page URL to give us more context, 
    specifically for user access flows."""

    def name(self) -> Text:
        return "action_set_current_url"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        current_url = None

        # find latest 'user' event
        latest_user_event = next(filter(is_user_event, reversed(tracker.events)), None)

        current_url = latest_user_event.get("metadata").get("current_url")

        if current_url:
            # overwrites the previous slot value
            return [SlotSet("current_url", current_url)]
        
        return []
