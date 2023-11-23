from typing import Text, Dict

import yaml
import os
from pathlib import Path


def add_intent(nlu: Dict, intent: Text, example: Text):
    if intent in nlu:
        content = nlu[intent]
    else:
        content = {
            "intent": intent,
            "examples": set()
        }
        nlu[intent] = content

    content.get("examples").add(example)


def main():
    nlu = {}
    for root, dirs, files in os.walk("./tests/stories"):
        for name in files:
            if name.endswith(".yml"):
                test_stories = yaml.load(open(f"{root}/{name}"), Loader=yaml.Loader)
                for test_story in test_stories.get("stories"):
                    for step in test_story.get("steps"):
                        if "user" in step and "intent" in step:
                            add_intent(nlu, step.get("intent"), step.get("user").strip())

    Path(".astro/nlu-from-stories").mkdir(parents=True, exist_ok=True)

    # From: https://github.com/yaml/pyyaml/issues/240#issuecomment-1096224358
    def str_presenter(dumper, data):
        """configures yaml for dumping multiline strings
        Ref: https://stackoverflow.com/questions/8640959/how-can-i-control-what-scalar-form-pyyaml-uses-for-my-data"""
        if data.count('\n') > 0:  # check for multiline string
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)

    yaml.add_representer(str, str_presenter)

    separator = "\n- "
    yaml.dump({
        "version": "3.1",
        "nlu": [{
            "intent": data.get("intent"),
            "examples": f"- {separator.join(data.get('examples'))}\n"
        } for data in nlu.values()]
        },
        stream=open(".astro/nlu-from-stories/test_data.yml", mode="w"),
        default_flow_style=False
    )


if __name__ == "__main__":
    main()



