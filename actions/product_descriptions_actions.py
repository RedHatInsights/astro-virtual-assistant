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

from common import logging
from common.header import Header
from common.requests import send_console_request

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
        product = next(tracker.get_latest_entity_values("product"), None)
        print(product)

        if product:
            response, result = await send_console_request(
                "chrome-service",
                "/api/chrome-service/v1/static/stable/prod/services/services.json",
                tracker
            )
            print("result: ", result)

            if not response.ok or not result:
                dispatcher.utter_message(
                    response="utter_image_builder_custom_content_error"
                )
                logger.debug(
                    "Failed to get a response from the content-sources API: status {}; result {}".format(
                        response.status, result
                    )
                )
                return
            
            service_match_options = []
            service_dict = {}

            for service in result:
                if service["title"] and service["description"]:
                    service_match_options.append(
                        FuzzySlotMatchOption(
                            service["title"],
                        )
                    )
                    service_dict[service["title"]] = service["description"]
                if service["links"]:
                    for link in service["links"]:
                        if "title" in link and "description" in link:
                            service_match_options.append(
                                FuzzySlotMatchOption(
                                    link["title"],
                                )
                            )
                            service_dict[link["title"]] = link["description"]

            service_match = FuzzySlotMatch(
                "",
                service_match_options,
            )

            print("service_match: ", service_match_options)

            print("service_dict: ", service_dict)

            resolved = resolve_slot_match(product, service_match, accepted_rate=60)

            print("resolved: ", resolved)

            # if response.status_code == 200:
            #     product_description = response.json()["description"]
            #     dispatcher.utter_message(text=product_description)
            # else:
            #     dispatcher.utter_message(
            #         text=f"Sorry, I couldn't find any description for {product}"
            #     )

        return [
            ActionExecuted(self.name()),
        ]
