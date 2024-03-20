from typing import Text, Dict, List

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


def _create_test_entity_extractor_with_reconciliation(
    config=None,
) -> FuzzyEntityExtractor:
    return FuzzyEntityExtractor(
        config if config is not None else FuzzyEntityExtractor.get_default_config(),
        object(),
        object(),
        [
            FuzzyEntities(
                "color_2",
                ["red", "green", "blue"],
                {
                    "light blue": "blue",
                    "navy blue": "blue",
                    "scarlet": "red",
                    "ruby red": "red",
                    "cherry red": "red",
                    "wine red": "red",
                    "greenish": "green",
                    "olive green": "green",
                    "sage green": "green",
                },
            )
        ],
    )


def _highlight(text: Text, entities: List[Dict]):
    """Helper, prints the before text and after text of a match. Used to debug"""
    for entity in entities:
        raw = text[entity[ENTITY_ATTRIBUTE_START] : entity[ENTITY_ATTRIBUTE_END]]
        before = text[
            entity[ENTITY_ATTRIBUTE_START] - 10 : entity[ENTITY_ATTRIBUTE_START]
        ]
        after = text[entity[ENTITY_ATTRIBUTE_END] : entity[ENTITY_ATTRIBUTE_END] + 10]
        print(f"{before}[{raw}]({entity[ENTITY_ATTRIBUTE_VALUE]}){after}")


def test_color_extraction():
    extractor = _create_test_entity_extractor()
    text = "Hello world I like red and cyan. Olive is also good color. I would like a large milkshake"
    entities = extractor.extract_entities(_create_message(text))
    _highlight(text, entities)

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
    text = "Hello world I like red and cyan. I found out that lapis lazuli is a synonym for blue. I would like a swandich of consderble size"
    entities = extractor.extract_entities(_create_message(text))
    _highlight(text, entities)

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
    text = "Hello world I like red and cyan. Olive is also good color."
    entities = extractor.extract_entities(_create_message(text))
    _highlight(text, entities)

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

    text = "Hello world I like red and cyan. olive is also good color."
    entities = extractor.extract_entities(_create_message(text))
    _highlight(text, entities)

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


def test_color_extraction_with_reconciliation():
    extractor = _create_test_entity_extractor_with_reconciliation()
    text = "I love blue, light blue and navy blue. I do also love red color, multiple shades of red like scarlet, ruby red, cherry red and even wine red. Green colors are my favorite such as olive green and sage green. I love red ruby too."
    entities = extractor.extract_entities(_create_message(text))
    _highlight(text, entities)

    assert len(entities) == 13
    assert entities[0] == {
        ENTITY_ATTRIBUTE_TYPE: "color_2",
        ENTITY_ATTRIBUTE_START: 7,
        ENTITY_ATTRIBUTE_END: 11,
        ENTITY_ATTRIBUTE_VALUE: "blue",
    }

    assert entities[1] == {
        ENTITY_ATTRIBUTE_TYPE: "color_2",
        ENTITY_ATTRIBUTE_START: 13,
        ENTITY_ATTRIBUTE_END: 23,
        ENTITY_ATTRIBUTE_VALUE: "blue",
    }

    assert entities[2] == {
        ENTITY_ATTRIBUTE_TYPE: "color_2",
        ENTITY_ATTRIBUTE_START: 28,
        ENTITY_ATTRIBUTE_END: 37,
        ENTITY_ATTRIBUTE_VALUE: "blue",
    }

    assert entities[3] == {
        ENTITY_ATTRIBUTE_TYPE: "color_2",
        ENTITY_ATTRIBUTE_START: 54,
        ENTITY_ATTRIBUTE_END: 57,
        ENTITY_ATTRIBUTE_VALUE: "red",
    }

    assert entities[4] == {
        ENTITY_ATTRIBUTE_TYPE: "color_2",
        ENTITY_ATTRIBUTE_START: 84,
        ENTITY_ATTRIBUTE_END: 87,
        ENTITY_ATTRIBUTE_VALUE: "red",
    }

    assert entities[5] == {
        ENTITY_ATTRIBUTE_TYPE: "color_2",
        ENTITY_ATTRIBUTE_START: 93,
        ENTITY_ATTRIBUTE_END: 100,
        ENTITY_ATTRIBUTE_VALUE: "red",
    }

    assert entities[6] == {
        ENTITY_ATTRIBUTE_TYPE: "color_2",
        ENTITY_ATTRIBUTE_START: 102,
        ENTITY_ATTRIBUTE_END: 110,
        ENTITY_ATTRIBUTE_VALUE: "red",
    }

    assert entities[7] == {
        ENTITY_ATTRIBUTE_TYPE: "color_2",
        ENTITY_ATTRIBUTE_START: 112,
        ENTITY_ATTRIBUTE_END: 122,
        ENTITY_ATTRIBUTE_VALUE: "red",
    }

    assert entities[8] == {
        ENTITY_ATTRIBUTE_TYPE: "color_2",
        ENTITY_ATTRIBUTE_START: 132,
        ENTITY_ATTRIBUTE_END: 140,
        ENTITY_ATTRIBUTE_VALUE: "red",
    }

    assert entities[9] == {
        ENTITY_ATTRIBUTE_TYPE: "color_2",
        ENTITY_ATTRIBUTE_START: 142,
        ENTITY_ATTRIBUTE_END: 147,
        ENTITY_ATTRIBUTE_VALUE: "green",
    }

    assert entities[10] == {
        ENTITY_ATTRIBUTE_TYPE: "color_2",
        ENTITY_ATTRIBUTE_START: 179,
        ENTITY_ATTRIBUTE_END: 190,
        ENTITY_ATTRIBUTE_VALUE: "green",
    }

    assert entities[11] == {
        ENTITY_ATTRIBUTE_TYPE: "color_2",
        ENTITY_ATTRIBUTE_START: 195,
        ENTITY_ATTRIBUTE_END: 205,
        ENTITY_ATTRIBUTE_VALUE: "green",
    }

    assert entities[12] == {
        ENTITY_ATTRIBUTE_TYPE: "color_2",
        ENTITY_ATTRIBUTE_START: 214,
        ENTITY_ATTRIBUTE_END: 217,
        ENTITY_ATTRIBUTE_VALUE: "red",
    }
