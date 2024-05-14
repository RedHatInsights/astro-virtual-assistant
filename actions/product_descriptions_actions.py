from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import (
    ActionExecuted,
    SlotSet,
    UserUtteranceReverted,
    ActionReverted,
)
from rasa_sdk.types import DomainDict

from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match
from actions.platform.chrome import create_service_options

from common import logging

logger = logging.initialize_logging()

class ProductDescription(Action):
    def name(self) -> Text:
        return "action_product_description"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        product = next(tracker.get_latest_entity_values("services_generated"), None)
        print(product)

        # remove console.redhat.com/ from the product name
        product = product.replace("console.redhat.com", "")

        if product:
            options = await create_service_options(tracker)
            if not options:
                dispatcher.utter_message(
                    response="utter_product_description_error",
                    product=product,
                )
                return
            fuzzy_options = [
                *map(
                    lambda o: FuzzySlotMatchOption(o["data"]["title"], o["synonyms"]),
                    options.values(),
                )
            ]
            match = FuzzySlotMatch("slot", fuzzy_options)
            resolved = resolve_slot_match(product, match)

            if len(resolved) > 0:
                if resolved["slot"] not in options or "data" not in options[resolved["slot"]]:
                    dispatcher.utter_message(
                        response="utter_product_description_error",
                        product=product,
                    )
                    return
                details = options[resolved["slot"]]["data"]
                
                if "title" not in details or "description" not in details:
                    dispatcher.utter_message(
                        response="utter_product_description_error",
                        product=product,
                    )
                    return
                dispatcher.utter_message(
                    response="utter_product_description",
                    product=details["title"],
                    description=details["description"],
                )

                if "href" in details:
                    dispatcher.utter_message(
                        response="utter_product_description_more",
                        product=details["title"],
                        href=details["href"],
                    )
            else:
                # can I send the bot to the next likelist intent?
                dispatcher.utter_message(
                    response="utter_product_description_error",
                    product=product,
                )

        return [
            ActionExecuted(self.name()),
        ]
