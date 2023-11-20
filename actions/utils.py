from os import getenv


def show_more(name: str, url_prefix: str):
    return {"show_more": {"name": name, "url_prefix": url_prefix}}


def get_is_running_locally() -> bool:
    return getenv("IS_RUNNING_LOCALLY", "false").lower() == "true"
