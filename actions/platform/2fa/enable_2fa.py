from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ActionExecuted

from common import logging
from common.config import app

logger = logging.initialize_logging()

_SLOT_IS_ORG_ADMIN = "is_org_admin"


class ActionEnable2fa(Action):
    def name(self) -> Text:
        return "action_enable_2fa"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        is_org_admin = tracker.get_slot(_SLOT_IS_ORG_ADMIN)

        if is_org_admin:
            dispatcher.utter_message(response="utter_user_is_org_admin")
        else:
            dispatcher.utter_message(response="utter_enable_2fa_individual_1")
            dispatcher.utter_message(response="utter_enable_2fa_individual_2")
            dispatcher.utter_message(response="utter_enable_2fa_individual_3")

        return [ActionExecuted(self.name())]


class ActionEnableOrg2FaCommand(Action):
    def name(self) -> Text:
        return "action_enable_org_2fa"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(
            response="utter_manage_org_2fa_command",
            enable_org_2fa="true",
            environment=app.environment_name,
        )

        return []
