from typing import Text, Dict, List, Any

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action
from rasa_sdk.events import SlotSet
from rasa_sdk.types import DomainDict


class ValidateFormClosing(FormValidationAction):
    def name(self) -> Text:
        return "validate_form_closing"

    async def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        if tracker.get_slot("requested_slot") == "closing_got_help":
            closing_got_help = tracker.get_slot("closing_got_help")
            if closing_got_help is True:
                dispatcher.utter_message(response="utter_closing_got_help_yes")
            elif closing_got_help is False:
                dispatcher.utter_message(response="utter_closing_got_help_no")

        return await super().run(dispatcher, tracker, domain)

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Text]:
        if tracker.get_slot("closing_leave_feedback") is False:
            updated_slots = domain_slots.copy()
            updated_slots.remove("closing_feedback")
            return updated_slots

        return domain_slots


class ExecuteFormClosing(Action):
    def name(self) -> Text:
        return "execute_form_closing"

    async def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        # Todo: Insert logic to send feedback
        if tracker.get_slot("closing_leave_feedback") is True:
            dispatcher.utter_message(response="utter_closing_share_feedback")
            print(f"Should send the following feedback:{tracker.get_slot('closing_feedback')}")

        dispatcher.utter_message(response="utter_closing_finally")
        return [SlotSet(key, None) for key in ["closing_got_help", "closing_leave_feedback", "closing_feedback"]]


class ExecuteFormClosingAnythingElse(Action):
    def name(self) -> Text:
        return "execute_form_closing_anything_else"

    async def run(
            self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        closing_anything_else = tracker.get_slot("closing_anything_else")
        if closing_anything_else is True:
            dispatcher.utter_message(response="utter_core_how_can_i_help")
        elif closing_anything_else is False:
            dispatcher.utter_message(response="utter_closing_bye")
        else:
            return []

        return [SlotSet(key, None) for key in ["closing_anything_else"]]
