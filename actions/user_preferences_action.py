from typing import Text, Dict, List, Any

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action

import logging

personal_info = ['email', 'email address', 'username', 'name', 'display name', 'address']

logger = logging.getLogger(__name__)
class ActionUserPreferences(Action):

    def name(self) -> Text:
        return "action_user_preferences"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        
        logging.error("This is an error message")

        entities = tracker.latest_message['entities']
        preference = None
        for e in entities:
            if e['entity'] == 'preference':
                preference = e['value']
        
        logging.error(preference)
        if preference in personal_info:
            logging.error("personal info")
            dispatcher.utter_message(text="You can change your " + preference + " and other personal information on redhat.com.")
        elif preference == 'password':
            logging.error("password")
            dispatcher.utter_message(id="utter_user_preferences_password")
            dispatcher.utter_message(id="utter_user_preferences_change_password")
            return []
        elif preference == 'login':
            logging.error("login")
            dispatcher.utter_message(id="utter_user_preferences_login")
            dispatcher.utter_message(id="utter_user_preferences_contact_support")
            return []
        else:
            logging.error("else")
            dispatcher.utter_message(id="utter_user_preferences_all")

        logging.error("after if")
        dispatcher.utter_message(id="utter_user_preferences_change_all")

        return []
