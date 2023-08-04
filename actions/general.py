# File for general actions, like greetings and more human-like responses.
from typing import Any, Text, Dict, List
from os import getenv

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ActionExecuted

import random
import math

people_talked_to: int = math.floor(random.random() * 2000000) + 1000000

class HowAreYou(Action):

    def name(self) -> Text:
        return 'action_how_are_you'

    async def run(self,
                  dispatcher: CollectingDispatcher,
                  tracker: Tracker,
                  domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global people_talked_to

        dispatcher.utter_message(text="It's been a long shift. I've talked to {:,} people and you!".format(people_talked_to))

        events = [ActionExecuted(self.name())]
        return events
