# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Text, List, Dict, Any

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.forms import Action
from rasa_sdk.types import DomainDict
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import EventType, SlotSet, ActiveLoop


class OpenshiftCreateClusterActionAskIsItCorrect(Action):
    def name(self) -> Text:
        return "action_ask_form_openshift_clusters_create-cluster_openshift_is_correct"

    def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[EventType]:
        slots = tracker.slots

        dispatcher.utter_message(text=f"""Great, thanks for that information. Here are your answers:
 - Where: {slots.get('openshift_where')}
 - Provider: {slots.get('openshift_provider')}
 - Managed by Red Hat: {slots.get('openshift_managed')}
 - Hosted or Standalone control plane?: {slots.get('openshift_hosted')}""")
        dispatcher.utter_message(text="Is this information correct?", buttons=[
            {
                "title": "Yes",
                "payload": "Yes"
            },
            {
                "title": "No",
                "payload": "No"
            }
        ])
        return []


class OpenshiftCreateClusterAction(FormValidationAction):

    def name(self) -> Text:
        return "validate_form_openshift_clusters_create-cluster"

    def validate_openshift_is_correct(self, slot_value: bool, dispatcher: CollectingDispatcher, tracker: Tracker,
                                        domain: DomainDict) -> Dict[Text, Any]:
        if slot_value is False:
            base_slots = self.base_slots()

            dispatcher.utter_message("OK. Lets try again.")
            return {slot: None for slot in base_slots}

        return {
            "openshift_is_correct": True
        }

    async def get_required_values(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict):
        return {required_slot_name: tracker.slots.get(required_slot_name) for required_slot_name in await self.required_slots(
            self.domain_slots(domain),
            dispatcher,
            tracker,
            domain
        )}

    async def missing_slots(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Text]:
        required_slots = await self.required_slots(self.domain_slots(domain), dispatcher, tracker, domain)
        return [
            slot_name
            for slot_name in required_slots
            if tracker.slots.get(slot_name) is None
        ]

    async def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[EventType]:
        required_values_before = await self.get_required_values(dispatcher, tracker, domain)
        result = await super().run(dispatcher, tracker, domain)

        required_values_are_equal = required_values_before == await self.get_required_values(dispatcher, tracker, domain)
        requested_slot = tracker.slots.get("requested_slot")

        is_missing_slots = len(await self.missing_slots(dispatcher, tracker, domain)) > 0

        if is_missing_slots:
            if required_values_are_equal and requested_slot is not None and tracker.slots.get(requested_slot) is None:
                dispatcher.utter_message(text="Sorry, I didn't understand. Can you rephrase your answer?")
        else:
            result.extend(self.process_slots(dispatcher, tracker.slots))

        return result

    def process_slots(self, dispatcher: CollectingDispatcher, slots: Dict[Text, Text]) -> List[EventType]:
        is_managed_and_hosted = slots.get("openshift_managed") == "yes" and slots.get("openshift_hosted") == "hosted"
        is_on_cloud = slots.get("openshift_where") == "cloud"
        provider = slots.get("openshift_provider")

        found = False

        if is_managed_and_hosted and is_on_cloud:
            base_response = "Ok. I recommend using "
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
        results = [SlotSet(slot, None) for slot in self.base_slots()]
        results.append(ActiveLoop(None))
        return results

    async def extract_openshift_hosted(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict):
        target_slot = "openshift_hosted"
        next_slot = tracker.slots.get("requested_slot")
        value = tracker.slots.get(target_slot)

        if next_slot == target_slot:
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
            "openshift_is_correct"
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

    def validate_openshift_where(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"openshift_where": slot_value}

    def validate_openshift_provider(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        if slot_value == "other":
            dispatcher.utter_message(
                text="I only know how to work with Amazon Web Services, Google Cloud, and Microsoft Azure."
            )
            return {"openshift_provider": None}

        return {"openshift_provider": slot_value}

    def validate_openshift_managed(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"openshift_managed": slot_value}

    def validate_openshift_hosted(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        return {"openshift_hosted": slot_value}
