from typing import Optional, List, Text

from rasa_sdk import FormValidationAction, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


async def form_action_is_starting(
    form: FormValidationAction,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: DomainDict,
):
    requested_slot = tracker.get_slot("requested_slot")
    if (
        requested_slot is None
        and not await all_required_slots_are_set(form, dispatcher, tracker, domain)
        and tracker.active_loop_name == form.form_name()
    ):
        return True

    return False


async def all_required_slots_are_set(
    form: FormValidationAction,
    dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: DomainDict,
    ignore: Optional[List[Text]] = None,
) -> bool:
    for slot in await form.required_slots(
        form.domain_slots(domain), dispatcher, tracker, domain
    ):
        if ignore is not None and slot in ignore:
            continue
        if tracker.get_slot(slot) is None:
            return False

    return True
