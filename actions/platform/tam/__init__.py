from typing import Tuple
from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption

_TAM_ACCOUNT_ID = "access_request_tam_account_id"
_TAM_ORG_ID = "access_request_tam_org_id"
_TAM_DURATION = "access_request_tam_duration"
_TAM_CONFIRMATION = "access_request_tam_confirmation"

_TAM_SLOTS = [_TAM_ACCOUNT_ID, _TAM_ORG_ID, _TAM_DURATION, _TAM_CONFIRMATION]

_DURATIONS = ["3 days", "1 week", "2 weeks"]

# trying to be simple and clever, could use a time parsing library
durations_match = FuzzySlotMatch(
    "access_request_tam_duration",
    [
        FuzzySlotMatchOption("3 days", ["days", "3", "three"]),
        FuzzySlotMatchOption("1 week", ["week", "1", "one"]),
        FuzzySlotMatchOption("2 weeks", ["weeks", "2", "two"]),
    ],
)


def get_start_end_date_from_duration(duration: str) -> Tuple[str, str]:
    from datetime import date, timedelta

    start_date = date.today()
    end_date = start_date

    if duration == "3 days":
        end_date += timedelta(days=3)
    elif duration == "1 week":
        end_date += timedelta(weeks=1)
    elif duration == "2 weeks":
        end_date += timedelta(weeks=2)

    return start_date.strftime("%m/%d/%Y"), end_date.strftime("%m/%d/%Y")
