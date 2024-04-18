from typing import List, Dict, Text, Any
from urllib.parse import urlparse

from rasa_sdk import FormValidationAction, Tracker, Action
from rasa_sdk.events import SlotSet, EventType, ActiveLoop
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict

from actions.slot_match import (
    FuzzySlotMatch,
    FuzzySlotMatchOption,
    resolve_slot_match,
    suggest_using_slot_match,
)
from actions.platform.chrome import (
    create_service_options,
    modify_favorite_service,
    get_user,
)
from actions.platform.favorites import (
    _FAVE_SERVICE,
    _FAVE_SUGGESTIONS,
    _FAVE_UNHAPPY,
    AbstractFavoritesForm,
)

class DeleteFavoritesForm(AbstractFavoritesForm):
    def name(self) -> str:
        return "validate_form_favorites_delete"

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
                buttons = self.create_suggestion_buttons(tracker)

                if len(buttons) > 0:
                    dispatcher.utter_message(
                        response="utter_favorites_delete_select", buttons=buttons
                    )
                else:
                    dispatcher.utter_message(response="utter_favorites_delete_select")
                return events + [SlotSet(_FAVE_SERVICE), SlotSet(_FAVE_SUGGESTIONS)]

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
                        # let's delete it
                        dispatcher.utter_message(
                            response="utter_favorites_delete_specified",
                            service=service["title"],
                            link=service["href"],
                            group=service["group"],
                        )

                        result = await modify_favorite_service(tracker, service, favorite=False)
                        if result.ok:
                            dispatcher.utter_message(
                                response="utter_favorites_delete_success",
                                service=service["title"],
                                link=service["href"],
                                group=service["group"],
                            )
                        else:
                            dispatcher.utter_message(
                                response="utter_favorites_delete_error",
                                service=service["title"],
                                link=service["href"],
                                group=service["group"],
                            )
                            events.append(SlotSet(_FAVE_UNHAPPY, True))
                        return events

                dispatcher.utter_message(
                    response="utter_favorites_delete_not_found",
                    service=service["title"],
                    link=service["href"],
                    group=service["group"],
                )
                events.append(SlotSet(_FAVE_UNHAPPY, True))
        
        elif tracker.get_slot(_FAVE_UNHAPPY):
            dispatcher.utter_message(response="utter_favorites_add_next")

        return events

    async def required_slots(
        self,
        domain_slots: List[Text],
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> List[Text]:
        return domain_slots
