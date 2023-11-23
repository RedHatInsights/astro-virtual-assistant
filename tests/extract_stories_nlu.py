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

    Path("nlu-from-stories").mkdir(exist_ok=True)

    separator = "\n- "
    yaml.dump({
        "version": "3.1",
        "nlu": [{
            "intent": data.get("intent"),
            "examples": f"- {separator.join(data.get('examples'))}"
        } for data in nlu.values()]
    }, stream=open("./nlu-from-stories/test_data.yml", mode="w"))


if __name__ == "__main__":
    main()



