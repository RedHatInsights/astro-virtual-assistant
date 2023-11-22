from typing import Text, Dict, List, Any

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action
from rasa_sdk.events import SlotSet

from common import metrics

class ActionPlatformShareFeedback(Action):
    def name(self) -> Text:
        return "action_platform_share_feedback"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        metrics.action_custom_action_count.labels(action_type=self.name()).inc()
        # Todo: Insert logic to send feedback to the platform
        return [SlotSet("platform_feedback", None)]

class ActionUserInterestShareEmail(Action):
    def name(self) -> Text:
        return "action_user_interest_share_email"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        metrics.action_custom_action_count.labels(action_type=self.name()).inc()
        # Todo: Insert logic to send the user's email
        return [SlotSet("user_interest_email", None)]
