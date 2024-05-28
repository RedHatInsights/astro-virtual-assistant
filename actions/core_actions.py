from typing import Text, Dict, List, Any

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action
from rasa_sdk.events import SlotSet, UserUtteranceReverted

from common import metrics, logging
from common.rasa.tracker import get_current_url, get_is_org_admin, get_is_internal

from common.config import app

_SLOT_FIRST_TIME_GREETING = "first_time_greeting"
_SLOT_CURRENT_URL = "current_url"
_SLOT_IS_ORG_ADMIN = "is_org_admin"
_SLOT_IS_INTERNAL = "is_internal"
_SLOT_BASE_CONSOLE_URL = "base_console_url"

_INTENT_CORE_SESSION_START = "intent_core_session_start"

logger = logging.initialize_logging()


class ActionBack(Action):
    """Revert the tracker state by one user utterances."""

    def name(self) -> Text:
        return "action_core_one_back"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        metrics.action_custom_action_count.labels(action_type=self.name()).inc()
        return [UserUtteranceReverted()]


class ActionPreProcess(Action):
    """Fired between calls to update slots"""

    def name(self) -> Text:
        return "action_core_pre_process"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        logger.info(f"Received {len(tracker.events)} events in tracker")
        metrics.action_custom_action_count.labels(action_type=self.name()).inc()

        results = []

        # Set the first_time_greeting slot to False on a user interaction
        if (
            tracker.get_slot(_SLOT_FIRST_TIME_GREETING)
            and tracker.get_intent_of_latest_message(True) != _INTENT_CORE_SESSION_START
        ):
            results.append(SlotSet(_SLOT_FIRST_TIME_GREETING, False))

        is_org_admin = get_is_org_admin(tracker)
        if is_org_admin != tracker.get_slot(_SLOT_IS_ORG_ADMIN):
            results.append(SlotSet(_SLOT_IS_ORG_ADMIN, is_org_admin))

        # Fetch the current_url from the request and set its slot if it's different
        current_url = get_current_url(tracker)
        if current_url and current_url != tracker.get_slot(_SLOT_CURRENT_URL):
            results.append(SlotSet(_SLOT_CURRENT_URL, current_url))

        base_console_url = tracker.get_slot(_SLOT_BASE_CONSOLE_URL)
        if base_console_url != app.console_dot_base_url:
            results.append(SlotSet(_SLOT_BASE_CONSOLE_URL, app.console_dot_base_url))

        is_internal = get_is_internal(tracker)
        if is_internal != tracker.get_slot(_SLOT_IS_INTERNAL):
            results.append(SlotSet(_SLOT_IS_INTERNAL, is_internal))

        return results
