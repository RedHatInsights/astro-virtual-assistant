# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Text, List, Optional, Dict, Any

from rasa_sdk import Tracker
from rasa_sdk.types import DomainDict
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import EventType, SlotSet
from .forms import IntentBasedFormValidationAction


class OpenshiftCreateClusterAction(IntentBasedFormValidationAction):

    def name(self) -> Text:
        return "validate_form_openshift_clusters_create-cluster"

    def utter_not_extracted(self, slot_name: Text) -> Optional[Text]:
        return "Sorry, I didn't understand. Can you rephrasing your answer?"

    def validate_openshift_need_changes(self, slot_value: bool, dispatcher: CollectingDispatcher, tracker: Tracker,
                                        domain: DomainDict) -> Dict[Text, Any]:
        if slot_value:
            base_slots = self.base_slots()

            dispatcher.utter_message("OK. Lets try again")
            return {slot: None for slot in base_slots}

        return {
            "openshift_need_changes": False
        }

    def form_finished(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict,
                      result: List[EventType]):
        slots = tracker.slots
        is_managed_and_hosted = slots.get("openshift_managed") == "yes" and slots.get("openshift_hosted") == "hosted"
        is_on_cloud = slots.get("openshift_where") == "cloud"
        provider = slots.get("openshift_provider")

        found = False

        dispatcher.utter_message(text=f"""Great, thanks for that information. Here are your answers:
 - Where: {slots.get('openshift_where')}
 - Provider: {slots.get('openshift_provider')}
 - Managed by Red Hat: {slots.get('openshift_managed')}
 - Hosted or Standalone control plane?: {slots.get('openshift_hosted')}""")

        if is_managed_and_hosted and is_on_cloud:
            base_response = "I recommend using "
            if provider == "aws":
                dispatcher.utter_message(text=base_response + "Red Hat OpenShift Service on AWS (ROSA).")
                link = "https://console.redhat.com/openshift/create/rosa/getstarted"
                dispatcher.utter_message(
                    text="You can visit the " +
                         f"[ROSA Getting Started page]({link}) to create your cluster there.")
                found = True
            elif provider == "azure":
                dispatcher.utter_message(text=base_response + "Azure Red Hat Openshift")
                found = True

        if not found:
            dispatcher.utter_message(text="Great, thanks for that information. I recommend using X.")

        # Clear slots
        result.append(SlotSet('openshift_where', None))
        result.append(SlotSet('openshift_provider', None))
        result.append(SlotSet('openshift_managed', None))
        result.append(SlotSet('openshift_hosted', None))

    async def extract_openshift_hosted(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict):
        next_slot = (await self.next_requested_slot(dispatcher, tracker, domain)).get("value")
        value = None

        if next_slot == "openshift_hosted":
            message = tracker.latest_message.get("text").lower()
            # Todo: Replace with embeddings
            if "standalone" in message:
                value = "standalone"
            elif "hosted" in message:
                value = "hosted"

        return {
            "openshift_hosted": value
        }

    @staticmethod
    def base_slots():
        return [
            "openshift_where",
            "openshift_provider",
            "openshift_managed",
            "openshift_hosted",
            "openshift_need_changes"
        ]

    async def required_slots(
            self,
            domain_slots: List[Text],
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> List[Text]:
        base_slots = self.base_slots()

        if tracker.slots.get("openshift_where") != "cloud":
            base_slots.remove("openshift_provider")

        return base_slots
