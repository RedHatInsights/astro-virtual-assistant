from typing import Text, Dict, List, Any

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action
from rasa_sdk.events import SlotSet

from common import logging

logger = logging.initialize_logging()

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
        for i in range(len(tracker.events) - 1, -1, -1):
            if tracker.events[i].get("event") == "user":
                current_url = tracker.events[i].get("metadata").get("current_url")
                break

        if current_url:
            # overwrites the previous slot value
            logger.info("setting current_url slot to " + current_url)
            return [SlotSet("current_url", current_url)]
        
        return [...]
