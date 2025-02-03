from common.config import config, log_config as _log_config

name = config("APP_NAME", default="virtual-assistant-watson-extension")
base_url = config("BASE_URL", default="/api/virtual-assistant-watson-extension/v2/")
port = config("PORT", default=5050, cast=int)


def log_config():
    import sys

    _log_config(sys.modules[__name__], print)
