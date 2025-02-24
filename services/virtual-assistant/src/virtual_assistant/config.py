from decouple import Choices
from common.config import config, log_config as _log_config
import logging

name = config("APP_NAME", default="virtual-assistant")
base_url = config("BASE_URL", default="/api/virtual-assistant/v2/")
port = config("PORT", default=5000, cast=int)
environment_name = config("ENVIRONMENT_NAME", default="stage", cast=str)

logger_type = config(
    "LOGGER_TYPE", default="basic", cast=Choices(["basic", "cloudwatch"])
)

console_dot_base_url = config(
    "CONSOLEDOT_BASE_URL", default="https://console.redhat.com"
)

# Session storage
session_storage = config(
    "SESSION_STORAGE", default="file", cast=Choices(["file", "redis"])
)
if session_storage == "redis":
    redis_hostname = config("REDIS_HOSTNAME")
    redis_port = config("REDIS_PORT")
    redis_username = config("REDIS_USERNAME")
    redis_password = config("REDIS_PASSWORD")

watson_api_url = config("WATSON_API_URL")
watson_api_key = config("WATSON_API_KEY")
watson_env_id = config("WATSON_ENV_ID")
watson_env_version = config(
    "WATSON_ENV_VERSION", default="2024-08-25"
)  # Needs updating if watson releases breaking change. See: https://cloud.ibm.com/apidocs/assistant-v2?code=python#versioning


def log_config():
    import sys

    _log_config(sys.modules[__name__], logging.getLogger(__name__).info)
