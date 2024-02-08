from typing import Text

from rasa.nlu.constants import TOKENS_NAMES
from rasa.nlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer
from rasa.shared.nlu.constants import (
    TEXT,
    ENTITY_ATTRIBUTE_TYPE,
    ENTITY_ATTRIBUTE_START,
    ENTITY_ATTRIBUTE_END,
    ENTITY_ATTRIBUTE_VALUE,
)
from rasa.shared.nlu.training_data.message import Message

from pipeline.fuzzy_entity_extractor import (
    FuzzyEntityExtractor,
    FuzzyEntities,
    CONFIG_CASE_SENSITIVE,
)


def _create_message(text: Text) -> Message:
    tokenizer = WhitespaceTokenizer(WhitespaceTokenizer.get_default_config())
    message = Message.build(text)
    tokens = tokenizer.tokenize(message, TEXT)
    message.set(TOKENS_NAMES[TEXT], tokens)
    return message


def _create_test_entity_extractor(config=None) -> FuzzyEntityExtractor:
    return FuzzyEntityExtractor(
        config if config is not None else FuzzyEntityExtractor.get_default_config(),
        object(),
        object(),
        [
            FuzzyEntities(
                "color",
                ["red", "green", "blue"],
                {
                    "cyan": "blue",
                    "lapis lazuli": "blue",
                    "magenta": "red",
                    "cherry": "red",
                    "scarlet": "red",
                    "pear": "green",
                    "olive": "green",
                },
            ),
            FuzzyEntities(
                "size",
                ["big", "small"],
                {
                    "large": "big",
                    "tiny": "small",
                    "huge": "big",
                    "immense": "big",
                    "of considerable size": "big",
                },
            ),
        ],
    )


def test_color_extraction():
    extractor = _create_test_entity_extractor()
    entities = extractor.extract_entities(
        _create_message(
            "Hello world I like red and cyan. Olive is also good color. I would like a large milkshake"
        )
    )

    assert len(entities) == 4
    assert entities[0] == {
        ENTITY_ATTRIBUTE_TYPE: "color",
        ENTITY_ATTRIBUTE_START: 19,
        ENTITY_ATTRIBUTE_END: 22,
        ENTITY_ATTRIBUTE_VALUE: "red",
    }

    assert entities[1] == {
        ENTITY_ATTRIBUTE_TYPE: "color",
        ENTITY_ATTRIBUTE_START: 27,
        ENTITY_ATTRIBUTE_END: 31,
        ENTITY_ATTRIBUTE_VALUE: "blue",
    }

    assert entities[2] == {
        ENTITY_ATTRIBUTE_TYPE: "color",
        ENTITY_ATTRIBUTE_START: 33,
        ENTITY_ATTRIBUTE_END: 38,
        ENTITY_ATTRIBUTE_VALUE: "green",
    }

    assert entities[3] == {
        ENTITY_ATTRIBUTE_TYPE: "size",
        ENTITY_ATTRIBUTE_START: 74,
        ENTITY_ATTRIBUTE_END: 79,
        ENTITY_ATTRIBUTE_VALUE: "big",
    }


def test_multi_word_color_extraction():
    """
    Tests the extraction of colors, multi words colors and multi words with typos ("of consderble size")
    :return:
    """
    extractor = _create_test_entity_extractor()
    entities = extractor.extract_entities(
        _create_message(
            "Hello world I like red and cyan. I found out that lapis lazuli is a synonym for blue. I would like a swandich of consderble size"
        )
    )

    # Sort entities to make them easier to assert
    entities.sort(key=lambda e: e[ENTITY_ATTRIBUTE_START])

    assert len(entities) == 5
    assert entities[0] == {
        ENTITY_ATTRIBUTE_TYPE: "color",
        ENTITY_ATTRIBUTE_START: 19,
        ENTITY_ATTRIBUTE_END: 22,
        ENTITY_ATTRIBUTE_VALUE: "red",
    }

    assert entities[1] == {
        ENTITY_ATTRIBUTE_TYPE: "color",
        ENTITY_ATTRIBUTE_START: 27,
        ENTITY_ATTRIBUTE_END: 31,
        ENTITY_ATTRIBUTE_VALUE: "blue",
    }

    assert entities[2] == {
        ENTITY_ATTRIBUTE_TYPE: "color",
        ENTITY_ATTRIBUTE_START: 50,
        ENTITY_ATTRIBUTE_END: 62,
        ENTITY_ATTRIBUTE_VALUE: "blue",
    }

    assert entities[3] == {
        ENTITY_ATTRIBUTE_TYPE: "color",
        ENTITY_ATTRIBUTE_START: 80,
        ENTITY_ATTRIBUTE_END: 84,
        ENTITY_ATTRIBUTE_VALUE: "blue",
    }

    assert entities[4] == {
        ENTITY_ATTRIBUTE_TYPE: "size",
        ENTITY_ATTRIBUTE_START: 110,
        ENTITY_ATTRIBUTE_END: 128,
        ENTITY_ATTRIBUTE_VALUE: "big",
    }


def test_case_sensitive_color_extraction():
    extractor = _create_test_entity_extractor({CONFIG_CASE_SENSITIVE: True})
    entities = extractor.extract_entities(
        _create_message("Hello world I like red and cyan. Olive is also good color.")
    )

    assert len(entities) == 2
    assert entities[0] == {
        ENTITY_ATTRIBUTE_TYPE: "color",
        ENTITY_ATTRIBUTE_START: 19,
        ENTITY_ATTRIBUTE_END: 22,
        ENTITY_ATTRIBUTE_VALUE: "red",
    }

    assert entities[1] == {
        ENTITY_ATTRIBUTE_TYPE: "color",
        ENTITY_ATTRIBUTE_START: 27,
        ENTITY_ATTRIBUTE_END: 31,
        ENTITY_ATTRIBUTE_VALUE: "blue",
    }

    entities = extractor.extract_entities(
        _create_message("Hello world I like red and cyan. olive is also good color.")
    )

    assert len(entities) == 3
    assert entities[0] == {
        ENTITY_ATTRIBUTE_TYPE: "color",
        ENTITY_ATTRIBUTE_START: 19,
        ENTITY_ATTRIBUTE_END: 22,
        ENTITY_ATTRIBUTE_VALUE: "red",
    }

    assert entities[1] == {
        ENTITY_ATTRIBUTE_TYPE: "color",
        ENTITY_ATTRIBUTE_START: 27,
        ENTITY_ATTRIBUTE_END: 31,
        ENTITY_ATTRIBUTE_VALUE: "blue",
    }
    assert entities[2] == {
        ENTITY_ATTRIBUTE_TYPE: "color",
        ENTITY_ATTRIBUTE_START: 33,
        ENTITY_ATTRIBUTE_END: 38,
        ENTITY_ATTRIBUTE_VALUE: "green",
    }
