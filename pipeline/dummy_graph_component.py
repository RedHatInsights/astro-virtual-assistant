from __future__ import annotations
import logging
from typing import Any, Dict, Text, List

from rasa.nlu.extractors.extractor import EntityExtractorMixin

from rasa.engine.graph import ExecutionContext, GraphComponent
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.storage.resource import Resource
from rasa.engine.storage.storage import ModelStorage
from rasa.shared.nlu.training_data.training_data import TrainingData
from rasa.shared.nlu.training_data.message import Message


logger = logging.getLogger(__name__)


@DefaultV1Recipe.register(
    DefaultV1Recipe.ComponentType.ENTITY_EXTRACTOR, is_trainable=True
)
class DummyGraphComponent(EntityExtractorMixin, GraphComponent):
    """Adds message features based on look up tables using fuzzy matching"""

    @classmethod
    def create(
        cls,
        config: Dict[Text, Any],
        model_storage: ModelStorage,
        resource: Resource,
        execution_context: ExecutionContext,
    ) -> DummyGraphComponent:
        """Creates a new untrained component"""
        return cls(resource)

    def __init__(self, resource: Resource):
        super().__init__()
        self.resource = resource

    def train(self, training_data: TrainingData) -> Resource:
        return self.resource

    def process(self, messages: List[Message]) -> List[Message]:
        return messages
