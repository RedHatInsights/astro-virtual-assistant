import sys
import traceback
from typing import Dict, Text, List, Optional

import yaml
import glob
import csv

class Flow:
    pass


class Intent:
    name: Text
    training: List[Text]
    yaml_filename: Text

    def __init__(self, name, training: List[Text], yaml_filename):
        self.name = name
        self.training = training
        self.yaml_filename = yaml_filename


class ResponseContent:
    text: Optional[Text]
    options: Optional[List[Text]]
    command: Optional[List[Text]]

    def __init__(
            self,
            text: Optional[Text],
            options: Optional[List[Text]],
            command: Optional[List[Text]]):
        self.text = text
        self.options = options
        self.command = command


class Response:
    name: Text
    contents: List[ResponseContent]
    yaml_filename: Text

    def __init__(self, name: Text, contents: List[ResponseContent], yaml_filename: Text):
        self.name = name
        self.contents = contents
        self.yaml_filename = yaml_filename


class DuplicatedDataFound(Exception):
    what: Text
    name: Text
    duplicated_filename: Text
    original_filename: Text

    def __init__(self, what: Text, name, duplicated_filename, original_filename):
        self.what = what
        self.name = name
        self.duplicated_filename = duplicated_filename
        self.original_filename = original_filename


class TrainingData:
    intents: Dict[Text, Intent]
    responses: Dict[Text, Response]
    flows: Dict[Text, Flow]

    def __init__(self):
        self.intents = dict[Text, Intent]()
        self.responses = dict[Text, Response]()
        self.flows = dict[Text, Flow]()

    def add_intent(self, name: Text, training: List[Text], filename: Text):
        if name in self.intents:
            raise DuplicatedDataFound("intent", name, filename, self.intents[name].yaml_filename)

        self.intents[name] = Intent(name, training, filename)

    def add_response(self, name: Text, data: Dict, filename: Text):
        if name in self.responses:
            raise DuplicatedDataFound("response", name, filename, self.responses[name].yaml_filename)

        self.responses[name] = Response(
            name,
            [
                ResponseContent(
                    text=content["text"] if "text" in content else None,
                    options=[
                        button["title"] for button in content["buttons"]
                    ] if "buttons" in content else None,
                    command=content["custom"]["command"] if "custom" in content else None
                ) for content in data
            ],
            filename
        )

    def __str__(self):
        return f"intents: {self.intents.__str__()}\n responses: {self.responses.__str__()}"


def process_nlu_entry(training_data: TrainingData, nlu_entry: dict, filename: Text):
    if 'intent' in nlu_entry:
        examples = nlu_entry['examples'] if 'examples' in nlu_entry else []
        if isinstance(examples, str):
            examples = [e.strip() for e in examples.split("-") if len(e.strip()) > 0]
        training_data.add_intent(nlu_entry['intent'], examples, filename)


def process_responses_entry(training_data: TrainingData, name: Text, data: Dict, filename: Text):
    training_data.add_response(name, data, filename)


if __name__ == "__main__":
    training_data = TrainingData()
    for yaml_filename in glob.iglob("./data/**/*.y*ml", recursive=True):
        if yaml_filename.lower().endswith(".yml") or yaml_filename.lower().endswith(".yaml"):
            try:
                with open(yaml_filename) as file:
                    file_contents = yaml.load(file, yaml.Loader)
                    if file_contents is not None:
                        if 'nlu' in file_contents:
                            for nlu_entry in file_contents['nlu']:
                                process_nlu_entry(training_data, nlu_entry, yaml_filename)
                        if 'responses' in file_contents:
                            for response_name, response_data in file_contents['responses'].items():
                                process_responses_entry(training_data, response_name, response_data, yaml_filename)
            except DuplicatedDataFound as ddf:
                print(f"Error processing file %{yaml_filename}: Found a duplicate {ddf.what} {ddf.name}")
                traceback.print_exc()
                exit(1)
            except Exception as exception:
                print(f"Error processing file %{yaml_filename}: {exception}")
                traceback.print_exc()
                exit(1)

    # Print intents to csv
    writer = csv.writer(sys.stdout)
    writer.writerow(['intent', 'training', 'filename'])
    for intent, data in training_data.intents.items():
        for training_entry in data.training:
            writer.writerow([data.name, training_entry, data.yaml_filename])
