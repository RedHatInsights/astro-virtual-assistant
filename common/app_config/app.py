from decouple import undefined as __undefined, Choices

from . import config as _config


console_dot_base_url = _config("CONSOLEDOT_BASE_URL", default="https://console.redhat.com")
requests_timeout = _config("TIMEOUT", default=5, cast=int)

app_name = _config("APP_NAME", default="astro-virtual-assistant")
group_id = _config("GROUP_ID", default=app_name)
api_listen_address = _config("API_LISTEN_ADDRESS", default="0.0.0.0")
api_url_expiry = _config("API_URL_EXPIRY", default=30, cast=int)
aws_region = _config("AWS_REGION", default="us-east-1")
log_level = _config("LOG_LEVEL", default="INFO", cast=Choices([
    "CRITICAL", "FATAL", "ERROR", "WARN", "INFO", "DEBUG"
]))

# Todo: Add namespace

hostname = _config("HOSTNAME", default=None)
prometheus = _config("PROMETHEUS", default=False, cast=bool)

# aws_access_key = config("AWS_ACCESS_KEY_ID", default=None)
# aws_secret_access_key = config()

is_running_locally = _config("IS_RUNNING_LOCALLY", default=False, cast=bool)
__optional_when_locally = __undefined if is_running_locally is False else None

logging_cloudwatch_access_key_id = _config("LOGGING_CLOUDWATCH_ACCESS_KEY_ID", default=__optional_when_locally)
logging_cloudwatch_secret_access_key = _config("LOGGING_CLOUDWATCH_ACCESS_KEY_ID", default=__optional_when_locally)
logging_cloudwatch_region = _config("LOGGING_CLOUDWATCH_REGION", default=__optional_when_locally)
logging_cloudwatch_log_group = _config("LOGGING_CLOUDWATCH_LOG_GROUP", default=__optional_when_locally)

advisor_url = _config("ENDPOINT__ADVISOR_BACKEND__API__URL", default=__optional_when_locally)
notifications_url = _config("ENDPOINT__NOTIFICATIONS_GW__SERVICE__URL", default=__optional_when_locally)
vulnerability_url = _config("ENDPOINT__VULNERABILITY_ENGINE__MANAGER_SERVICE__URL", default=__optional_when_locally)

# Todo: Changed from DB_HOST
database_host = _config("DB_HOSTNAME", default=None)
database_port = _config("DB_PORT", default=None, cast=int)
# Todo: Changed from DB_USER
database_user = _config("DB_USERNAME", default=None)
database_password = _config("DB_PASSWORD", default=None)
database_name = _config("DB_NAME", default=None)

# Todo: Update changed from DB_SSLMODE
database_ssl_mode = _config("DB_SSL_MODE", default=None)

lock_store_type = _config("LOCK_STORE_TYPE", default="in_memory")

__redis_config_default = None if lock_store_type == "in_memory" else __undefined

# Todo: Changed from REDIS_URL
redis_url = _config("REDIS_HOSTNAME", default=__redis_config_default)
redis_port = _config("REDIS_PORT", default=__redis_config_default)
redis_username = _config("REDIS_USERNAME", default=__redis_config_default)
redis_password = _config("REDIS_PASSWORD", default=__redis_config_default)
# Todo: Check if we need REDIS_DB
