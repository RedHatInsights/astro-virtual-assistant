from decouple import undefined as __undefined, Choices
import os

try:
    from rasa.constants import DEFAULT_RASA_PORT
except ModuleNotFoundError:
    # Rasa is not installed in actions and internal server - Default to 0
    DEFAULT_RASA_PORT = 0

from . import config as _config

name = _config("APP_NAME", default="astro-virtual-assistant")

dev_offline_refresh_token = _config("OFFLINE_REFRESH_TOKEN", default=None)
dev_sso_refresh_token_url = _config(
    "SSO_REFRESH_TOKEN_URL",
    default=None,
)

not_set_base_url = "https://not-set.com"
console_dot_base_url = _config(
    "CONSOLEDOT_BASE_URL", default="https://console.redhat.com"
)
requests_timeout = _config("TIMEOUT", default=5, cast=int)

app_name = _config("APP_NAME", default="astro-virtual-assistant")
group_id = _config("GROUP_ID", default=app_name)
api_listen_address = _config("API_LISTEN_ADDRESS", default="0.0.0.0")
api_url_expiry = _config("API_URL_EXPIRY", default=30, cast=int)
aws_region = _config("AWS_REGION", default="us-east-1")
log_level = _config(
    "LOG_LEVEL",
    default="INFO",
    cast=Choices(["CRITICAL", "FATAL", "ERROR", "WARN", "INFO", "DEBUG"]),
)

namespace = _config("NAMESPACE", default=None)

hostname = _config("HOSTNAME", default=None)
prometheus = _config("PROMETHEUS", default=False, cast=bool)

prometheus_port = _config("METRICS_PORT", default=0, cast=int)
api_port = _config(
    "API_PORT", default=_config("PUBLIC_PORT", default=DEFAULT_RASA_PORT), cast=int
)
actions_port = _config(
    "ACTIONS_PORT", default=_config("PRIVATE_PORT", default=0), cast=int
)
internal_api_port = _config(
    "INTERNAL_API_PORT", default=_config("PRIVATE_PORT", default=8083), cast=int
)

is_running_locally = _config("IS_RUNNING_LOCALLY", default=False, cast=bool)
__optional_when_locally = __undefined if is_running_locally is False else None
fail_fast_on_dependencies = _config(
    "FAIL_FAST_ON_DEPENDENCIES", default=True, cast=bool
)

__endpoint_default = __undefined
if is_running_locally:
    __endpoint_default = console_dot_base_url
elif fail_fast_on_dependencies is False:
    __endpoint_default = not_set_base_url
    print(f"Dependencies are not required, using {__endpoint_default} as default.")

environment_name = _config("ENVIRONMENT_NAME", default="stage", cast=str)

logging_cloudwatch_access_key_id = _config(
    "LOGGING_CLOUDWATCH_ACCESS_KEY_ID", default=__optional_when_locally
)
logging_cloudwatch_secret_access_key = _config(
    "LOGGING_CLOUDWATCH_SECRET_ACCESS_KEY", default=__optional_when_locally
)
logging_cloudwatch_region = _config(
    "LOGGING_CLOUDWATCH_REGION", default=__optional_when_locally
)
logging_cloudwatch_log_group = _config(
    "LOGGING_CLOUDWATCH_LOG_GROUP", default=__optional_when_locally
)
logging_cloudwatch_create_log_group = _config(
    "AWS_CREATE_LOG_GROUP", default=True, cast=bool
)
logging_cloudwatch_log_stream = _config("AWS_LOG_STREAM", default=os.uname().nodename)


advisor_url = _config("ENDPOINT__ADVISOR_BACKEND__API__URL", default=__endpoint_default)
advisor_openshift_url = _config(
    "ENDPOINT__CCX_SMART_PROXY__SERVICE__URL",
    default=__endpoint_default,
)
notifications_gw_url = _config(
    "ENDPOINT__NOTIFICATIONS_GW__SERVICE__URL", default=__endpoint_default
)
notifications_url = _config(
    "ENDPOINT__NOTIFICATIONS_BACKEND__SERVICE__URL", default=__endpoint_default
)
chrome_service_url = _config(
    "ENDPOINT__CHROME_SERVICE__API__URL", default=__endpoint_default
)
rbac_url = _config("ENDPOINT__RBAC__SERVICE__URL", default=__endpoint_default)

sources_url = _config("ENDPOINT__SOURCES_API__SVC__URL", default=__endpoint_default)

vulnerability_url = _config(
    "ENDPOINT__VULNERABILITY_ENGINE__MANAGER_SERVICE__URL", default=__endpoint_default
)
content_sources_url = _config(
    "ENDPOINT__CONTENT_SOURCES_BACKEND__SERVICE__URL", default=__endpoint_default
)
rhsm_url = _config("ENDPOINT__RHSM_API_PROXY__SERVICE__URL", default=__endpoint_default)

actions_url = _config(
    "PRIVATE_ENDPOINT__VIRTUAL_ASSISTANT__ACTIONS__URL", default="http://localhost:5055"
)

tracker_store_type = _config("TRACKER_STORE_TYPE", default="InMemoryTrackerStore")
database_host = _config("DB_HOSTNAME", default=None)
database_port = _config("DB_PORT", default=0, cast=int)
database_user = _config("DB_USERNAME", default=None)
database_password = _config("DB_PASSWORD", default=None)
database_name = _config("DB_NAME", default=None)
database_ssl_mode = _config("DB_SSL_MODE", default=None)
database_ca_path = _config("DB_CA_PATH", default=None)

lock_store_type = _config("LOCK_STORE_TYPE", default="in_memory")

redis_hostname = _config("REDIS_HOSTNAME", default=None)
redis_port = _config("REDIS_PORT", default=None)
redis_username = _config("REDIS_USERNAME", default=None)
redis_password = _config("REDIS_PASSWORD", default=None)


def log_config():
    import logging
    import sys

    primitives = (bool, str, int, float, type(None))

    def is_primitive(obj):
        return isinstance(obj, primitives)

    def should_log(key, value) -> bool:
        if not is_primitive(value):
            return False

        if key.startswith("_"):
            return False

        return True

    def get_value(key: str, value) -> str:
        if value is None or (
            isinstance(value, int) and not isinstance(value, bool) and value == 0
        ):
            return f"--not-set-- ({value})"

        upper_key = key.upper()
        accepted_variables = ["dev_sso_refresh_token_url"]
        if (
            any(
                banned in upper_key for banned in ["PASSWORD", "TOKEN", "SECRET", "KEY"]
            )
            and key not in accepted_variables
        ):
            return "*********"

        return str(value)

    for k, v in sys.modules[__name__].__dict__.items():
        if should_log(k, v):
            logging.info(f"Using {k}: {get_value(k, v)}")
