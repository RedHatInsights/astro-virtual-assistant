import os
import signal
import sys


from prometheus_client import start_http_server
from threading import Event

from rasa.constants import DEFAULT_RASA_PORT
from sanic.log import LOGGING_CONFIG_DEFAULTS

from common import logging
from common.config import app

from rasa.__main__ import main as rasa_main

logger = None

event = Event()


def start_prometheus():
    start_http_server(app.prometheus_port)


def handle_signal(signal, frame):
    event.set()


signal.signal(signal.SIGTERM, handle_signal)


def set_endpoints_config_variables():
    os.environ["ACTIONS_ENDPOINT_URL"] = app.actions_url + "/webhook"
    os.environ["TRACKER_STORE_TYPE"] = app.tracker_store_type
    os.environ["DB_HOSTNAME"] = app.database_host or ""
    os.environ["DB_PORT"] = (
        str(app.database_port) if app.database_port is not None else ""
    )
    os.environ["DB_NAME"] = app.database_name or ""
    os.environ["DB_USERNAME"] = app.database_user or ""
    os.environ["DB_PASSWORD"] = app.database_password or ""
    os.environ["LOCK_STORE_TYPE"] = app.lock_store_type
    os.environ["REDIS_HOSTNAME"] = app.redis_hostname or ""
    os.environ["REDIS_PORT"] = str(app.redis_port) if app.redis_port is not None else ""
    os.environ["REDIS_DB"] = "1"


def main():
    global logger

    logger = logging.initialize_logging()

    logger.info("Starting Astro")

    app.log_config()
    set_endpoints_config_variables()

    if app.prometheus is True:
        start_prometheus()

    # Use API_PORT when set to other than default
    if app.api_port != DEFAULT_RASA_PORT:
        sys.argv.extend(["--port", str(app.api_port)])

    # Rasa sets a default config, but we've already configured the environment
    # Override their default config, enabling
    # Enable incremental logging to prevent our logging from being closed
    LOGGING_CONFIG_DEFAULTS["incremental"] = True
    LOGGING_CONFIG_DEFAULTS["loggers"] = {}
    LOGGING_CONFIG_DEFAULTS["handlers"] = {}
    LOGGING_CONFIG_DEFAULTS["formatters"] = {}

    rasa_main()


if __name__ == "__main__":
    main()
