from os import getenv


def get_is_running_locally() -> bool:
    return getenv("IS_RUNNING_LOCALLY", "false").lower() == "true"
