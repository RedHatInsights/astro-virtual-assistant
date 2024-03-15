from typing import List, Optional, Text

from rasa_sdk import Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict


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
