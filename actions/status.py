from typing import Text, Dict, List, Any

from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action
import requests

class ActionServicesOffline(Action):

    def name(self) -> Text:
        return "action_services_offline"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:

        try:
            result = requests.get(
                "https://status.redhat.com/api/v2/incidents/unresolved.json"
            ).json()
        except Exception as e:
            print(f"An Exception occured while handling response from status.redhat.com: {e}")

        if not result or not result['incidents']:
            dispatcher.utter_message(text="I was unable to talk with status.redhat.com to fulfill your request.")
            return []
        
        incidents = result['incidents']
        count = str(len(incidents))
        if incidents and count != "0":
            dispatcher.utter_message(text="I'm sorry, but we are experiencing " + count + " incident(s).")

            for incident in incidents:
                dispatcher.utter_message(text=incident['name'] + " is currently " + incident['status'] + ".")

            dispatcher.utter_message("Visit [status.redhat.com](status.redhat.com) for further outage information.")
        else:
            dispatcher.utter_message(text="All services seem to be operating normally.")
            dispatcher.utter_message(text="Visit [status.redhat.com](https://status.redhat.com) for more information on Red Hat outages and maintenance.")
        
        return []
