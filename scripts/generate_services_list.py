# the NLU needs concrete examples for services
# - pull the list of services from the chrome service API
# - add the services to the data/domain-generated.yml file (slots.services-generated.values)

from rasa.shared.core.trackers import DialogueStateTracker
from unittest.mock import Mock

from actions.platform.chrome import create_list_of_services
import asyncio

DESCRIPTION_INTENT = "intent_product_description"


def mock_tracker():
    tracker = Mock(spec=DialogueStateTracker)

    tracker.sender_id = "generate_services_list"
    tracker.latest_message = None

    return tracker


def ignore_services_without_descriptions(services: list[str]):
    return [service for service in services if "description" in service]


def create_entity_list(services: list[str]):
    list = []
    for service in services:
        list.append(service["title"])
        list.append(service["href"])
        list.append("console.redhat.com" + service["href"])
        list += service["alt_title"]
    return list


async def add_services_to_domain(services: list[str]):
    import sys
    import ruamel.yaml

    yaml = ruamel.yaml.YAML()
    with open("data/domain-generated.yml") as fp:
        data = yaml.load(fp)
    data["slots"]["services_generated"]["values"] = services
    yaml.dump(data, sys.stdout)
    with open("data/domain-generated.yml", "w") as fp:
        yaml.dump(data, fp)


async def add_services_to_description_nlu(services: list[str]):
    import sys
    import ruamel.yaml
    import re

    yaml = ruamel.yaml.YAML()
    with open("data/descriptions/nlu.yml") as fp:
        data = yaml.load(fp)

    for item in data["nlu"]:
        intent = item["intent"]
        if intent != DESCRIPTION_INTENT:
            continue
        examples = item["examples"].split("\n")[:10]

        for service in services:
            formatted_service = service.lstrip("/").rstrip("/")
            formatted_service = re.sub(
                r"\(.*?\)", "", formatted_service
            ).strip()  # fix the formatting for what is [Remote Host Configuration (RHC)](services_generated)
            formatted_service = formatted_service.split("(")[0]
            examples.append(
                "- what is [{service}](services_generated)".format(
                    service=formatted_service
                )
            )
        item["examples"] = "\n".join(examples)
        print(item["examples"])

    yaml.dump(data, sys.stdout)
    with open("data/descriptions/nlu.yml", "w") as fp:
        yaml.dump(data, fp)


async def main():
    tracker = mock_tracker()
    services = await create_list_of_services(tracker)
    services = ignore_services_without_descriptions(services)
    services = create_entity_list(services)
    await add_services_to_domain(services)
    await add_services_to_description_nlu(services)


if __name__ == "__main__":
    asyncio.run(main())
