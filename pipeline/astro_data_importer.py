from pathlib import Path
from typing import Optional, Text, Union, List

from rasa.shared.importers.importer import TrainingDataImporter
from rasa.shared.importers.rasa import RasaFileImporter
import rasa.shared.data
from rasa.shared.nlu.training_data.formats.rasa_yaml import KEY_NLU
import rasa.shared.utils.io


class AstroDataImporter(RasaFileImporter):
    def __init__(
        self,
        config_file: Optional[Text] = None,
        domain_path: Optional[Text] = None,
        training_data_paths: Optional[Union[List[Text], Text]] = None,
    ):
        super().__init__(config_file, domain_path, training_data_paths)

        # Remove nlu files with responses. That promotes duplicates responses as
        # domain files are being mistaken by NLU files because of the response key
        self._nlu_files = rasa.shared.data.get_data_files(
            training_data_paths, self.is_yaml_nlu_file
        )

    @staticmethod
    def is_yaml_nlu_file(file_path: Text) -> bool:
        if Path(file_path).suffix.lower() not in {".yml", ".yaml"}:
            return False

        return rasa.shared.utils.io.is_key_in_yaml(file_path, KEY_NLU)
