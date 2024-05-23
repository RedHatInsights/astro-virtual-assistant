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
        FuzzySlotMatchOption(
            "3 days", ["days", "3", "three"]
        ),
        FuzzySlotMatchOption(
            "1 week", ["week", "1", "one"]
        ),
        FuzzySlotMatchOption(
            "2 weeks", ["weeks", "2", "two"]
        ),
    ],
)
