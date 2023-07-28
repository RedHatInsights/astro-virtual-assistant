from abc import abstractmethod
from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Tracker
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.types import DomainDict
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import EventType


class IntentBasedFormValidationAction(FormValidationAction):

    @abstractmethod
    def name(self) -> Text:
        """Unique identifier of this simple action."""
        raise NotImplementedError("An action must implement a name")

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> List[EventType]:
        result = await super().run(dispatcher, tracker, domain)

        form_finished = getattr(self, 'form_finished', None)
        has_all_slots = (await self.next_requested_slot(dispatcher, tracker, domain)).get("value") is None
        if form_finished is not None and has_all_slots:
            form_finished(dispatcher, tracker, domain, result)

        return result

    def utter_not_extracted(self, slot_name: Text) -> Optional[Text]:
        return None

    """Returns the intent that started the active loop if there is any"""
    def get_trigger_intent(self, tracker: Tracker) -> Text:
        if tracker.active_loop:
            return tracker.active_loop["trigger_message"]["intent"]["name"]

        # No active-loop. Assume current intent is the one triggering this loop
        return tracker.get_intent_of_latest_message()

    async def get_extraction_events(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict
    ) -> List[EventType]:
        slots_to_extract = await self.required_slots(
            self.domain_slots(domain), dispatcher, tracker, domain
        )
        next_slot = None

        for slot in slots_to_extract:
            if tracker.slots.get(slot) is None:
                next_slot = slot
                break

        extraction_events = await super().get_extraction_events(dispatcher, tracker, domain)

        if next_slot is not None and \
                tracker.slots.get(next_slot) is None and \
                tracker.get_intent_of_latest_message() != self.get_trigger_intent(tracker):
            utterance = self.utter_not_extracted(next_slot)
            if utterance is not None:
                dispatcher.utter_message(text=utterance)

        return extraction_events

    def _generate_extract_slot(self, slot_name: Text):
        async def extract_slot(dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict):
            intent = tracker.get_intent_of_latest_message()
            if intent == self.get_trigger_intent(tracker):
                return {slot_name: tracker.slots.get(slot_name)}

            expected_intent_start = f"intent_{slot_name}_"
            previous_slot_value = tracker.slots.get(slot_name)
            found_intent_value = None

            if intent.startswith(expected_intent_start):
                found_intent_value = intent[len(expected_intent_start):]

            return {
                slot_name: found_intent_value or previous_slot_value
            }
        return extract_slot

    async def _extract_slot(
            self,
            slot_name: Text,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        # To avoid issues - lets prevent from overwriting a slot once it has been set.
        if tracker.slots.get(slot_name) is not None:
            return {
                slot_name: tracker.slots.get(slot_name)
            }

        method_name = f"extract_{slot_name.replace('-', '_')}"

        if not getattr(self, method_name, None):
            mappings = domain.get("slots").get(slot_name).get("mappings")

            if len(list(filter(lambda m: m.get("type") == "custom", mappings))) > 0:
                setattr(self, method_name, self._generate_extract_slot(slot_name))

        return await super()._extract_slot(slot_name, dispatcher,  tracker, domain)
