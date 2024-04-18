from typing import List, Dict, Text, Any
from urllib.parse import urlparse

from rasa_sdk import FormValidationAction, Tracker, Action
from rasa_sdk.events import SlotSet, EventType, ActiveLoop
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions.platform.chrome import (
    add_service_to_favorites,
    get_user,
)
from actions.platform.favorites import (
    _FAVE_SERVICE,
    _FAVE_SUGGESTIONS,
    AbstractFavoritesForm,
)

from common.requests import send_console_request


class AddFavoritesForm(AbstractFavoritesForm):
    def name(self) -> str:
        return "validate_form_favorites_add"

    async def run(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> List[EventType]:
        events = await super().run(dispatcher, tracker, domain)
        requested_slot = tracker.get_slot("requested_slot")

        if requested_slot == _FAVE_SERVICE:
            service = tracker.get_slot(_FAVE_SERVICE)
            if service == "unsure":
                return events
            if service == None:
                suggestions = tracker.get_slot(_FAVE_SUGGESTIONS)
                if suggestions:
                    buttons = []
                    for suggestion in suggestions:
                        suggest = suggestion["value"]
                        buttons.append(
                            {
                                "title": f'{suggest["title"]} ({suggest["group"]})',
                                "payload": suggest["href"],
                            }
                        )

                    dispatcher.utter_message(
                        response="utter_favorites_add_select", buttons=buttons
                    )
                else:
                    dispatcher.utter_message(response="utter_favorites_add_select")
                return events + [SlotSet(_FAVE_SERVICE)]

            # check that the service is not already favorited
            response, content = await get_user(tracker)
            if (
                response.ok
                and content
                and content.get("data")
                and "favoritePages" in content.get("data")
            ):
                favorites = content.get("data")["favoritePages"]

                for favorite in favorites:
                    if (
                        favorite.get("favorite")
                        and favorite.get("pathname") == service["href"]
                    ):
                        dispatcher.utter_message(
                            response="utter_favorites_add_already",
                            service=service["title"],
                            link=service["href"],
                            group=service["group"],
                        )
                        return events

            dispatcher.utter_message(
                response="utter_favorites_add_specified",
                service=service["title"],
                link=service["href"],
                group=service["group"],
            )
            result = await add_service_to_favorites(tracker, service)
            if result.ok:
                dispatcher.utter_message(
                    response="utter_favorites_add_success",
                    service=service["title"],
                    link=service["href"],
                    group=service["group"],
                )
            else:
                dispatcher.utter_message(
                    response="utter_favorites_add_failed",
                    service=service["title"],
                    link=service["href"],
                    group=service["group"],
                )

        return events

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Text]:
        return domain_slots
