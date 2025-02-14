from common.config import config, log_config as _log_config
from decouple import Csv, Choices
import logging

name = config("APP_NAME", default="virtual-assistant-watson-extension")
base_url = config("BASE_URL", default="/api/virtual-assistant-watson-extension/v2/")
port = config("PORT", default=5050, cast=int)

logger_type = config("LOGGER_TYPE", default="basic", cast=Choices(['basic', 'cloudwatch']))

authentication_type = config("AUTHENTICATION_TYPE", default="no-auth", cast=Choices(['no-auth', 'api-key']))
api_keys = config("API_KEYS", default=None, cast=Csv(str))

# Session storage
session_storage = config("SESSION_STORAGE", default="file")
redis_hostname = config("REDIS_HOSTNAME", default=None)
redis_port = config("REDIS_PORT", default=None)
redis_username = config("REDIS_USERNAME", default=None)
redis_password = config("REDIS_PASSWORD", default=None)


def log_config():
    import sys

    _log_config(sys.modules[__name__], logging.getLogger(__name__).info)
