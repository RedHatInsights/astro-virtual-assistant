import pytest
from actions.slot_match import FuzzySlotMatch, FuzzySlotMatchOption, resolve_slot_match


@pytest.mark.parametrize("user_message", ["rhel", "RHEL", "RhEl", "RHel", "rHeL", "rhel1", "rhel8", "rhel9"])
def test_simple_slot_match(user_message: str):
    resolved = resolve_slot_match(
        user_message,
        FuzzySlotMatch(
            "system",
            [
                FuzzySlotMatchOption("rhel"),
                FuzzySlotMatchOption("foobar")
            ]
        )
    )

    assert resolved is not None
    assert "system" in resolved
    assert resolved["system"] is "rhel"


@pytest.mark.parametrize("user_message", ["google", "Google", "GOOGLE"])
def test_sub_options_slot_match(user_message: str):
    resolved = resolve_slot_match(
        "google",
        FuzzySlotMatch(
            "integration_type",
            [
                FuzzySlotMatchOption("cloud"),
                FuzzySlotMatchOption("communications", sub_options=FuzzySlotMatch(
                    "communications_type",
                    [
                        FuzzySlotMatchOption("google"),
                        FuzzySlotMatchOption("teams"),
                        FuzzySlotMatchOption("slack"),
                    ]
                ))
            ]
        )
    )

    assert resolved is not None
    assert "integration_type" in resolved
    assert "communications_type" in resolved
    assert resolved["integration_type"] is "communications"
    assert resolved["communications_type"] is "google"


def test_slot_match_with_synonyms():
    setting = FuzzySlotMatch(
        "system",
        [
            FuzzySlotMatchOption("rhel", ["rhel", "red hat"]),
            FuzzySlotMatchOption("foobar", ["baz"])
        ]
    )

    resolved = resolve_slot_match("rhel", setting)
    assert resolved is not None
    assert "system" in resolved
    assert resolved["system"] is "rhel"

    resolved = resolve_slot_match("red hat", setting)
    assert resolved is not None
    assert "system" in resolved
    assert resolved["system"] is "rhel"

    resolved = resolve_slot_match("baz", setting)
    assert resolved is not None
    assert "system" in resolved
    assert resolved["system"] is "foobar"

    resolved = resolve_slot_match("foobar", setting)
    assert resolved is not None
    assert "system" not in resolved
