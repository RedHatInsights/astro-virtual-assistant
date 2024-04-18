import json

from actions.slot_match import FuzzySlotMatchOption
from common.requests import send_console_request

unsure_option = FuzzySlotMatchOption(
    {"href": "unsure", "title": "unsure", "group": "unsure"},
    [
        "not sure",
        "unsure",
        "idk",
        "I'm not sure",
        "no clue",
        "I have no idea",
        "other",
        "I don't know the name of the service",
        "I don't know",
        "other",
    ],
)


async def get_user(tracker):
    # struggles to be a json response, manually doing it here
    resp = await send_console_request(
        "chrome-service",
        "/api/chrome-service/v1/user",
        tracker,
        "get",
    )

    response, content = resp
    print(content)

    return response, json.loads(content)


async def create_service_options(tracker) -> list[FuzzySlotMatchOption]:
    response, content = await get_generated_services(tracker)
    if response.ok:
        return parse_generated_services(content)
    else:
        # failed to reach the chrome service
        return [unsure_option]


def parse_generated_services(content):
    options = [unsure_option]
    for category in content:
        for link in category["links"]:
            group_title = link.get("title")
            if "isGroup" in link and link["isGroup"]:
                for sublink in link["links"]:
                    if "isExternal" in sublink and sublink["isExternal"]:
                        # not really a service
                        continue
                    synonyms = []
                    value = {"group": group_title}

                    if "href" not in sublink:
                        # path needs to be here to be favorited
                        continue
                    synonyms.append(sublink["href"])
                    value["href"] = sublink["href"]

                    if "title" in sublink:
                        value["title"] = sublink["title"]
                        synonyms.append(sublink["title"])
                    if "appId" in sublink:
                        value["app_id"] = sublink["appId"]
                        synonyms.append(sublink["appId"])
                    if "alt_title" in sublink:
                        synonyms += sublink["alt_title"]
                    options.append(FuzzySlotMatchOption(value, synonyms))
    return options


async def get_generated_services(tracker):
    return await send_console_request(
        "chrome-service",
        "/api/chrome-service/v1/static/stable/prod/services/services-generated.json",
        tracker,
        "get",
    )


async def add_service_to_favorites(tracker, service):
    print(f"Adding service {service} to favorites")
    if service is None or "href" not in service:
        return
    return await send_console_request(
        "chrome-service",
        "/api/chrome-service/v1/favorite-pages",
        tracker,
        method="post",
        json={
            "favorite": True,
            "pathname": service["href"],
        },
        fetch_content=False,
    )
