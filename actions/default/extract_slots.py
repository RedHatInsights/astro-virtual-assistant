from typing import Text, Dict, List, Any

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action
from rasa_sdk.events import SlotSet

from common import logging

logger = logging.initialize_logging()

class ActionExtractSlots(Action):
    """Add metadata from the incoming request to custom slots"""

    def name(self) -> Text:
        return "action_extract_slots"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        
        # take the metadata (current_url) from the incoming request and put it in a slot
        

        logger.error("action_extract_slots")
        logger.error(tracker.slots)
        
        current_url = tracker.get_slot("session_started_metadata").get("current_url")

        logger.info("current_url: " + str(current_url))
        if current_url:
            # overwrites the previous slot value
            return [SlotSet("current_url", current_url)]
        else:
            return [...]
