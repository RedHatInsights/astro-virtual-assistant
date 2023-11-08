from typing import Text, Dict, List, Any

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action
from rasa_sdk.events import SlotSet

from common import metrics
from .utils import is_user_event

class ActionSetIsOrgAdmin(Action):

    def name(self) -> Text:
        return "action_set_is_org_admin"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        metrics.action_custom_action_count.labels(action_type=self.name()).inc()

        # if the value is already set, don't overwrite it
        if tracker.get_slot("is_org_admin") is not None:
            return []

        is_org_admin = False
        try:
            # get the last event from the tracker
            is_org_admin = tracker.events[-1].get("metadata").get("is_org_admin")
        except Exception as e:
            print(f"An Exception occured while handling retrieving is_org_admin: {e}")
            is_org_admin = False

        return [SlotSet("is_org_admin", is_org_admin)]


class ActionSetCurrentURL(Action):
    """Sets the user's current page URL to give us more context,
    specifically for user access flows."""

    def name(self) -> Text:
        return "action_set_current_url"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        metrics.action_custom_action_count.labels(action_type=self.name()).inc()

        # find latest 'user' event
        latest_user_event = next(filter(is_user_event, reversed(tracker.events)), None)

        if latest_user_event is None:
            return []

        current_url = latest_user_event.get("metadata").get("current_url")

        if current_url and current_url != tracker.get_slot("current_url"):
            # overwrites the previous slot value
            return [SlotSet("current_url", current_url)]

        return []
