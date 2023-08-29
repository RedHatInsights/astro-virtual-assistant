from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, Text, Type

import jsonpickle
from rasa.nlu.extractors.extractor import EntityExtractorMixin
from rasa.nlu.tokenizers.tokenizer import Tokenizer

import rasa.shared.utils.io
import rasa.utils.io
import rasa.nlu.utils.pattern_utils as pattern_utils
from rasa.engine.graph import ExecutionContext, GraphComponent
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.nlu.constants import TOKENS_NAMES
from rasa.shared.nlu.constants import TEXT, ENTITIES, ENTITY_ATTRIBUTE_TYPE, \
    ENTITY_ATTRIBUTE_START, ENTITY_ATTRIBUTE_VALUE, ENTITY_ATTRIBUTE_END
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.message import Message

from rapidfuzz import process, fuzz

logger = logging.getLogger(__name__)

FUZZY_ENTITIES_FILENAME = "fuzzy_entities.pkl"

CONFIG_SENTENCE_SCORE_CUTOFF = 'sentence_score_cutoff'
CONFIG_WORD_SCORE_CUTOFF = 'word_score_cutoff'
CONFIG_CASE_SENSITIVE = 'case_sensitive'


class FuzzyEntities:
    name: Text
    entity_list: List[Text]
    value_mapping: Dict[Text, Text]

    def __init__(self, name: Text, entity_list: Optional[List[Text]] = None, synonyms: Optional[Dict[Text, Text]] = None):
        if entity_list is None:
            entity_list = []
        if synonyms is None:
            synonyms = {}

        self.name = name
        self.entity_list = entity_list.copy()
        self.entity_list.extend(
            [synonym for synonym, entity in synonyms.items() if entity in entity_list]
        )

        self.value_mapping = {entity: synonyms[entity] for entity in self.entity_list if entity in synonyms}

    def get_value_of(self, entity: Text) -> Text:
        if entity in self.value_mapping:
            return self.value_mapping[entity]

        return entity


@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.ENTITY_EXTRACTOR, is_trainable=True
)
class FuzzyEntityExtractor(EntityExtractorMixin, GraphComponent):
    """Adds message features based on look up tables using fuzzy matching"""

    fuzzy_entities: List[FuzzyEntities]
    sentence_score_cutoff: float
    word_score_cutoff: float
    case_sensitive: bool

    @classmethod
    def required_components(cls) -> List[Type]:
        return [Tokenizer]

    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        """The component's default config"""
        return {
            # Score used to check if a sentence contains any of the words - it should be a lower score than the
            # word score as the scorer will yield higher score on a word-to-word basis
            CONFIG_SENTENCE_SCORE_CUTOFF: 55,
            # Score used to check if a word is part of the choices.
            CONFIG_WORD_SCORE_CUTOFF: 75,
            # If the matching is case sensitive
            CONFIG_CASE_SENSITIVE: False
        }

    def __init__(
            self,
            config: Dict[Text, Any],
            model_storage: ModelStorage,
            resource: Resource,
            fuzzy_entities_list: Optional[List[FuzzyEntities]] = None
    ) -> None:
        """Fetches the lookup tables information"""
        super().__init__()
        self._config = {**self.get_default_config(), **config}
        self._model_storage = model_storage
        self._resource = resource
        self.fuzzy_entities = fuzzy_entities_list if fuzzy_entities_list else []
        self.sentence_score_cutoff = self._config[CONFIG_SENTENCE_SCORE_CUTOFF]
        self.word_score_cutoff = self._config[CONFIG_WORD_SCORE_CUTOFF]
        self.case_sensitive = self._config[CONFIG_CASE_SENSITIVE]

    @classmethod
    def create(
            cls,
            config: Dict[Text, Any],
            model_storage: ModelStorage,
            resource: Resource,
            execution_context: ExecutionContext,
    ) -> FuzzyEntityExtractor:
        """Creates a new untrained component"""
        return cls(config, model_storage, resource)

    def train(self, training_data: TrainingData) -> Resource:
        """Train the component with all know look up tables"""
        for lookup_table in training_data.lookup_tables:
            lookup_elements = lookup_table["elements"]

            if not isinstance(lookup_elements, list):
                lookup_elements = pattern_utils.read_lookup_table_file(lookup_elements)

            self.fuzzy_entities.append(FuzzyEntities(
                lookup_table["name"],
                list(map(self._process_text, lookup_elements)),
                {
                    self._process_text(synonym): self._process_text(entity)
                    for synonym, entity in training_data.entity_synonyms.items()
                }
            ))

        if not self.fuzzy_entities:
            rasa.shared.utils.io.raise_warning(
                "No lookup tables found."
            )

        self._persist()
        return self._resource

    def process(self, messages: List[Message]) -> List[Message]:
        """Extract entities from messages and appends them to the attribute

        Returns:
          the given list of messages that have been modified in-place
        """
        for message in messages:
            self.process_message(message)

        return messages

    def process_message(self, message: Message) -> None:
        extracted_entities = self.extract_entities(message)
        self.add_extractor_name(extracted_entities)
        message.set(
            ENTITIES,
            message.get(ENTITIES, []) + extracted_entities,
            add_to_output=True
        )

    def extract_entities(
            self, message: Message
    ) -> List[Dict[Text, Any]]:
        """Process the message to find entities.
        The algorithm tries to find the matches from the lookup tables using fuzzy search
        It tries the whole message first and then it goes token by token to find the match.
        The first goal is to use only one word and we might eventually add other heuristics
        to support multiple words.
        """

        entities = []

        tokens = None
        if self.fuzzy_entities and message.get(TEXT):
            tokens = message.get(TOKENS_NAMES[TEXT], [])

        if not tokens:
            return []

        for fuzzy_entity in self.fuzzy_entities:
            fuzzy_result_list = process.extract(
                self._process_text(message.get(TEXT)),
                fuzzy_entity.entity_list,
                score_cutoff=self.sentence_score_cutoff
            )

            if len(fuzzy_result_list) > 0:
                for token in tokens:
                    for fuzzy_result in fuzzy_result_list:
                        ratio = fuzz.QRatio(
                            self._process_text(token.text),
                            fuzzy_result[0]
                        )
                        if ratio >= self.word_score_cutoff:
                            entities.append({
                                ENTITY_ATTRIBUTE_TYPE: fuzzy_entity.name,
                                ENTITY_ATTRIBUTE_START: token.start,
                                ENTITY_ATTRIBUTE_END: token.end,
                                ENTITY_ATTRIBUTE_VALUE: fuzzy_entity.get_value_of(fuzzy_result[0])
                            })

        return entities

    def _process_text(self, text: Text):
        if self.case_sensitive:
            return text

        return text.lower()

    @classmethod
    def load(
            cls,
            config: Dict[Text, Any],
            model_storage: ModelStorage,
            resource: Resource,
            execution_context: ExecutionContext,
            **kwargs: Any,
    ) -> FuzzyEntityExtractor:
        """Loads trained component."""
        fuzzy_entities = None

        try:
            with model_storage.read_from(resource) as model_dir:
                fuzzy_entities_file = model_dir / FUZZY_ENTITIES_FILENAME
                fuzzy_entities = jsonpickle.decode(rasa.shared.utils.io.read_json_file(fuzzy_entities_file))
        except (ValueError, FileNotFoundError):
            logger.warning(
                f"Failed to load `{cls.__class__.__name__}` from model storage. "
                f"Resource '{resource.name}' doesn't exist."
            )

        return cls(
            config,
            model_storage,
            resource,
            fuzzy_entities_list=fuzzy_entities,
        )

    def _persist(self) -> None:
        with self._model_storage.write_to(self._resource) as model_dir:
            fuzzy_entities_file = model_dir / FUZZY_ENTITIES_FILENAME

            rasa.shared.utils.io.dump_obj_as_json_to_file(
                fuzzy_entities_file,
                jsonpickle.encode(self.fuzzy_entities, unpicklable=True)
            )

    @classmethod
    def validate_config(cls, config: Dict[Text, Any]) -> None:
        """Validates that the component is configured properly."""
        pass
