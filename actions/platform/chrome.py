import json

from actions.slot_match import FuzzySlotMatchOption
from common.requests import send_console_request


async def get_user(tracker):
    # struggles to be a json response, manually doing it here
    resp = await send_console_request(
        "chrome-service",
        "/api/chrome-service/v1/user",
        tracker,
        "get",
    )

    response, content = resp

    return response, json.loads(content)


async def create_service_options(tracker) -> list[FuzzySlotMatchOption]:
    response, content = await get_generated_services(tracker)
    if response.ok:
        services = parse_generated_services(content)

        options = {}
        for service in services:
            if "href" not in service:
                # path needs to be here to be favorited
                continue
            options[service["title"]] = convert_service_to_option(service)

        return options
    else:
        # failed to reach the chrome service
        return []


async def create_list_of_services(tracker) -> list:
    response, content = await get_generated_services(tracker)
    if response.ok:
        services = parse_generated_services(content)
        return services
    else:
        # failed to reach the chrome service
        print("Failed to reach the chrome service")
        return []


def parse_generated_services(content):
    services = []
    for category in content:
        for link in category["links"]:
            group_title = link.get("title")
            if "isGroup" in link and link["isGroup"]:
                for sublink in link["links"]:
                    if "isExternal" in sublink and sublink["isExternal"]:
                        # not really a service
                        continue
                    service = {"group": group_title}

                    if "href" in sublink:
                        service["href"] = sublink["href"]
                    if "title" in sublink:
                        service["title"] = sublink["title"]
                    if "appId" in sublink:
                        service["app_id"] = sublink["appId"]
                    if "description" in sublink:
                        service["description"] = sublink["description"]
                    service["alt_title"] = sublink.get("alt_title", [])
                    services.append(service)
    return services


async def get_generated_services(tracker):
    return await send_console_request(
        "chrome-service",
        "/api/chrome-service/v1/static/stable/prod/services/services-generated.json",
        tracker,
        "get",
    )


def convert_service_to_option(service):
    value = {"group": service["group"]}
    synonyms = [service["href"]]
    value["href"] = service["href"]

    if "title" in service:
        value["title"] = service["title"]
        synonyms.append(service["title"])
    if "appId" in service:
        value["app_id"] = service["appId"]
        synonyms.append(service["appId"])
    if "alt_title" in service:
        synonyms += service["alt_title"]
    if "description" in service:
        value["description"] = service["description"]
    return {
        "data": value,
        "synonyms": synonyms,
    }


async def modify_favorite_service(tracker, service, favorite=True):
    if service is None or "href" not in service:
        return
    return await send_console_request(
        "chrome-service",
        "/api/chrome-service/v1/favorite-pages",
        tracker,
        method="post",
        json={
            "favorite": favorite,
            "pathname": service["href"],
        },
        fetch_content=False,
    )
