from __future__ import annotations
import logging
from typing import Any, Dict, List, Optional, Text, Tuple, Type
import numpy as np
import scipy.sparse
from rasa.nlu.tokenizers.tokenizer import Tokenizer

import rasa.shared.utils.io
import rasa.utils.io
import rasa.nlu.utils.pattern_utils as pattern_utils
from rasa.engine.graph import ExecutionContext, GraphComponent
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.nlu.constants import TOKENS_NAMES
from rasa.nlu.featurizers.sparse_featurizer.sparse_featurizer import SparseFeaturizer
from rasa.shared.nlu.constants import TEXT, RESPONSE, ACTION_TEXT
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.message import Message

from rapidfuzz import process, fuzz

logger = logging.getLogger(__name__)

FUZZY_ENTITIES_FILENAME = "fuzzy_featurizer.pkl"


@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.MESSAGE_FEATURIZER, is_trainable=True
)
class FuzzyFeaturizer(SparseFeaturizer, GraphComponent):
    """Adds message features based on look up tables using fuzzy matching"""

    @classmethod
    def required_components(cls) -> List[Type]:
        return [Tokenizer]

    @staticmethod
    def get_default_config() -> Dict[Text, Any]:
        return {**SparseFeaturizer.get_default_config()}

    def __init__(
        self,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
        know_fuzzy_entities: Optional[List[Dict[Text, Any]]] = None,
    ) -> None:
        """Fetches the lookup tables information"""
        super().__init__(execution_context.node_name, config)
        self._model_storage = model_storage
        self._resource = resource
        self.know_fuzzy_entities = know_fuzzy_entities if know_fuzzy_entities else []
        self.finetune_mode = execution_context.is_finetuning

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> FuzzyFeaturizer:
        """Creates a new untrained component (see parent class for full docstring"""
        return cls(config, model_storage, resource, execution_context)

    def train(self, training_data: TrainingData) -> Resource:
        """Trains the component with all know look up tables"""

        # This would be the place to use if we want to do pre-computing
        # i.e. if we were transforming words to vectors, we would do it here

        for lookup_table in training_data.lookup_tables:
            lookup_elements = lookup_table["elements"]

            if not isinstance(lookup_elements, list):
                lookup_elements = pattern_utils.read_lookup_table_file(lookup_elements)

            # Load synonyms
            # Dedupe ?
            # Remove stop words ?
            self.know_fuzzy_entities.append(
                {"name": lookup_table["name"], "elements": lookup_elements}
            )

        self._persist()
        return self._resource

    def process_training_data(self, training_data: TrainingData) -> TrainingData:
        for example in training_data.training_examples:
            for attribute in [TEXT, RESPONSE, ACTION_TEXT]:
                self.process_message(example, attribute)

        return training_data

    def process(self, messages: List[Message]) -> List[Message]:
        """Featurizes all given messages in-place

        Returns:
          the given list of messages which have been modified in-place
        """
        for message in messages:
            print(message.get(TEXT))
            self.process_message(message, TEXT)

        return messages

    def process_message(self, message: Message, attribute: Text) -> None:
        if message.get(TEXT) is not None and "policy" in message.get(TEXT).lower():
            print(message.get(TEXT))

        if attribute == TEXT and message.get(attribute) is not None:
            print(message.get(attribute))

        features_list = self._features_for_fuzzy_entities(message, attribute)

        if features_list is None:
            return

        for [sequence_features, sentence_features] in features_list:
            self.add_features_to_message(
                sequence_features, sentence_features, attribute, message
            )

    def _features_for_fuzzy_entities(
        self, message: Message, attribute: Text
    ) -> Optional[List[Tuple[scipy.sparse.coo_matrix, scipy.sparse.coo_matrix]]]:
        """Process the message to find entities.
        The algorithm tries to find the matches from the lookup tables using fuzzy search
        It tries the whole message first and then it goes token by token to find the match.
        The first goal is to use only one word and we might eventually add other heuristics
        to support multiple words.
        """

        tokens = None
        if self.know_fuzzy_entities and message.get(attribute):
            tokens = message.get(TOKENS_NAMES[attribute], [])

        if not tokens:
            return None

        sequence_length = len(tokens)
        # num_entity_types = len(self.know_fuzzy_entities)

        features: List[Tuple[scipy.sparse.coo_matrix, scipy.sparse.coo_matrix]] = []

        for fuzzy_entity_index, fuzzy_entity in enumerate(self.know_fuzzy_entities):
            fuzzy_result_list = process.extract(
                message.get(attribute), fuzzy_entity["elements"], score_cutoff=55
            )

            num_options = len(fuzzy_entity["elements"])

            sequence_features = np.zeros([sequence_length, num_options])
            sentence_features = np.zeros([1, num_options])

            # ADapt to handle synonyms
            if len(fuzzy_result_list) > 0:
                for token_index, token in enumerate(tokens):
                    fuzzy_entities = token.get("fuzzy_entities", default={})
                    fuzzy_entities[fuzzy_entity["name"]] = False

                    for fuzzy_result in fuzzy_result_list:
                        ratio = fuzz.QRatio(token.text, fuzzy_result[0])
                        if ratio > 0.75:
                            fuzzy_entities[fuzzy_entity["name"]] = fuzzy_result[0]
                            sequence_features[token_index][fuzzy_result[2]] = 1.0
                            if attribute in [RESPONSE, TEXT, ACTION_TEXT]:
                                # sentence vector should contain all patterns
                                sentence_features[0][fuzzy_result[2]] = 1.0

                    token.set("fuzzy_entities", fuzzy_entities)

            if message.get(TEXT) is not None and "policy" in message.get(TEXT).lower():
                print((sentence_features, sentence_features))
            features.append(
                (
                    scipy.sparse.coo_matrix(sequence_features),
                    scipy.sparse.coo_matrix(sentence_features),
                )
            )

        return features

    @classmethod
    def load(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
        **kwargs: Any,
    ) -> FuzzyFeaturizer:
        """Loads trained component."""
        know_fuzzy_entities = None

        try:
            with model_storage.read_from(resource) as model_dir:
                fuzzy_entities_file = model_dir / FUZZY_ENTITIES_FILENAME
                know_fuzzy_entities = rasa.shared.utils.io.read_json_file(
                    fuzzy_entities_file
                )
        except (ValueError, FileNotFoundError):
            logger.warning(
                f"Failed to load `{cls.__class__.__name__}` from model storage. "
                f"Resource '{resource.name}' doesn't exist."
            )

        return cls(
            config,
            model_storage,
            resource,
            execution_context,
            know_fuzzy_entities=know_fuzzy_entities,
        )

    def _persist(self) -> None:
        with self._model_storage.write_to(self._resource) as model_dir:
            fuzzy_entities_file = model_dir / FUZZY_ENTITIES_FILENAME
            rasa.shared.utils.io.dump_obj_as_json_to_file(
                fuzzy_entities_file, self.know_fuzzy_entities
            )

    @classmethod
    def validate_config(cls, config: Dict[Text, Any]) -> None:
        """Validates that the component is configured properly."""
        pass
