from typing import Text, Dict, List, Any

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action

personal_info = [
    "email",
    "email address",
    "username",
    "name",
    "display name",
    "address",
]


class ActionUserPreferences(Action):
    def name(self) -> Text:
        return "action_user_preferences"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message["entities"]
        preference = None
        for e in entities:
            if e["entity"] == "preference":
                preference = e["value"]

        if preference in personal_info:
            dispatcher.utter_message(
                response="utter_user_preferences_specific", preference=preference
            )
        elif preference == "password":
            dispatcher.utter_message(
                response="utter_user_preferences_specific", preference="password"
            )
            dispatcher.utter_message(
                response="utter_user_preferences_password_redirect"
            )
            return []
        elif preference == "login":
            dispatcher.utter_message(response="utter_user_preferences_login")
            dispatcher.utter_message(response="utter_user_preferences_contact_support")
            return []
        else:
            dispatcher.utter_message(response="utter_user_preferences_all")

        dispatcher.utter_message(response="utter_user_preferences_all_redirect")

        return []
