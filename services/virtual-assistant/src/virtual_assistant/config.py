from decouple import undefined as __undefined
from common.config import config, log_config as _log_config

name = config("APP_NAME", default="virtual-assistant")
base_url = config("BASE_URL", default="/api/virtual-assistant/v2/")
port = config("PORT", default=5000, cast=int)
environment_name = config("ENVIRONMENT_NAME", default="stage", cast=str)

console_dot_base_url = config(
    "CONSOLEDOT_BASE_URL", default="https://console.redhat.com"
)

session_storage = config("SESSION_STORAGE", default="file")
__redis_defaults = None if session_storage == "file" else __undefined

redis_hostname = config("REDIS_HOSTNAME", default=__redis_defaults)
redis_port = config("REDIS_PORT", default=__redis_defaults)
redis_username = config("REDIS_USERNAME", default=__redis_defaults)
redis_password = config("REDIS_PASSWORD", default=__redis_defaults)

watson_api_url = config("WATSON_API_URL", default=None)
watson_api_key = config("WATSON_API_KEY", default=None)
watson_env_id = config("WATSON_ENV_ID", default=None)
watson_env_version = config(
    "WATSON_ENV_VERSION", default="2024-08-25"
)  # Needs updating if watson releases breaking change. See: https://cloud.ibm.com/apidocs/assistant-v2?code=python#versioning

def log_config():
    import sys

    _log_config(sys.modules[__name__], print)
