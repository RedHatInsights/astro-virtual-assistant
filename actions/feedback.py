from typing import Text, Dict, List, Any

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action
from rasa_sdk.types import DomainDict
from rasa_sdk.events import SlotSet


class CancelledEarly(Action):
    """User is done with their questions early."""

    def name(self) -> Text:
        return "action_cancelled_early"

    async def run(
        self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> List[Dict[Text, Any]]:
        return [SlotSet("feedback_anything_else", False)]

class ValidateFeedbackForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_feedback_form"
    
    @staticmethod
    def base_slots():
        return ["feedback_rating", "feedback_anything_else", "feedback_additional_comment_question", "feedback_additional_comment"]

    async def required_slots(self, domain_slots: List[Text], dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[Text]:
        base_slots = domain_slots.copy()

        if tracker.slots.get("feedback_anything_else") is True: # user has more to chat about
            base_slots.remove("feedback_additional_comment_question")
            base_slots.remove("feedback_additional_comment")
        
        if tracker.slots.get("feedback_additional_comment_question") is False:
            base_slots.remove("feedback_additional_comment")
        
        return base_slots

    async def process_slots(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: DomainDict) -> List[EventType]:
        # store the feedback in the database here
        return []
        
            
    async def validate_feedback_rating(self, slot_value: bool, dispatcher: CollectingDispatcher, tracker: Tracker,
                                        domain: DomainDict) -> Dict[Text, Any]:
        if slot_value is False:
            dispatcher.utter_message(template="utter_feedback_rating_yes")
        else:
            dispatcher.utter_message(template="utter_feedback_rating_no")

        return {"feedback_rating": slot_value}
    
    async def validate_feedback_additional_comment_question(self, slot_value: bool, dispatcher: CollectingDispatcher, tracker: Tracker,
                                        domain: DomainDict) -> Dict[Text, Any]:
        if slot_value is False:
            return {"feedback_additional_comment": None}
        
        return {"feedback_additional_comment_question": slot_value}
        
    async def validate_feedback_additional_comment(self, slot_value: str, dispatcher: CollectingDispatcher, tracker: Tracker,
                                        domain: DomainDict) -> Dict[Text, Any]:
        if slot_value is None:
            # prompt user for additional comment again
            dispatcher.utter_message(template="utter_feedback_additional_comment_question")
        else:
            dispatcher.utter_message(template="utter_feedback_additional_comment_submitted")
            dispatcher.utter_message(template="utter_feedback_final")
        
        return {"feedback_additional_comment": slot_value}
    

