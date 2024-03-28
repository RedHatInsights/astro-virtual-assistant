from typing import List, Optional, Dict

from rapidfuzz import fuzz

ACCEPTED_RATIO = 80


class FuzzySlotMatch:
    slot: str
    options: List["FuzzySlotMatchOption"]

    def __init__(self, slot: str, options: List["FuzzySlotMatchOption"]):
        self.slot = slot
        self.options = options


class FuzzySlotMatchOption:
    value: str
    synonyms: List[str]
    sub_options: Optional[FuzzySlotMatch]

    def __init__(
        self,
        value: str,
        synonyms: Optional[List[str]] = None,
        sub_options: Optional[FuzzySlotMatch] = None,
    ):
        self.value = value
        self.synonyms = (
            [s.lower() for s in synonyms]
            if synonyms is not None
            else [self.value.lower()]
        )
        self.sub_options = sub_options


def _sanitize_input(user_message: str) -> str:
    return user_message.lower()


def resolve_slot_match(
    user_message: str, slot_match: FuzzySlotMatch, accepted_rate=ACCEPTED_RATIO
) -> Dict[str, any]:
    user_message = _sanitize_input(user_message)
    for options in slot_match.options:
        for value in options.synonyms:
            ratio = fuzz.QRatio(user_message, value)
            if ratio >= accepted_rate:
                return {slot_match.slot: options.value}

        if options.sub_options is not None:
            resolved_child = resolve_slot_match(
                user_message, options.sub_options, accepted_rate=accepted_rate
            )

            if len(resolved_child) > 0:
                resolved_child[slot_match.slot] = options.value
                return resolved_child

    return {}
