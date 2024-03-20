from typing import Text, Dict, List, Any

import aiohttp
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action

from common import metrics


class ActionServicesOffline(Action):
    def name(self) -> Text:
        return "action_services_offline"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        metrics.action_custom_action_count.labels(action_type=self.name()).inc()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://status.redhat.com/api/v2/incidents/unresolved.json"
                ) as status_response:
                    result = await status_response.json()
        except Exception as e:
            print(
                f"An Exception occured while handling response from status.redhat.com: {e}"
            )

        if not (result and "incidents" in result):
            dispatcher.utter_message(response="utter_services_offline_error")
            return []

        incidents = result["incidents"]
        count = str(len(incidents))
        if incidents and count != "0":
            dispatcher.utter_message(
                response="utter_services_offline_incidents", count=count
            )

            for incident in incidents:
                dispatcher.utter_message(
                    response="utter_services_offline_info",
                    name=incident["name"],
                    status=incident["status"],
                )

            dispatcher.utter_message(response="utter_services_offline_further_info")
        else:
            dispatcher.utter_message(response="utter_services_offline_no_incidents")
            dispatcher.utter_message(response="utter_services_offline_more_info")

        return []
