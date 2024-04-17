from common.requests import send_console_request

from actions.slot_match import FuzzySlotMatchOption
from common.requests import send_console_request

unsure_option = FuzzySlotMatchOption(
    "unsure",
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

async def create_service_options(tracker) -> list[FuzzySlotMatchOption]:
    response, content = await get_generated_services(tracker)
    if response.ok:
        return parse_generated_services(content)
    else:
        # failed to reach the chrome service
        return [unsure_option]

def parse_generated_services(content):
    options = [unsure_option]
    print(content)
    for category in content:
        for link in category['links']:
            if "isGroup" in link and link["isGroup"]:
                for sublink in link['links']:
                    synonyms = []
                    value = {}
                    if "href" in sublink:
                        synonyms.append(sublink["href"])
                    else:
                        # needs to be here to add it as a favorite
                        continue

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

async def get_user_favorites(tracker):
    return await send_console_request(tracker, "GET", "/api/chrome-service/v1/user")

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
