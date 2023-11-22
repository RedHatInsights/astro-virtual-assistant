import os
import signal
import sys


from prometheus_client import start_http_server
from threading import Event
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
    os.environ["ACTIONS_ENDPOINT_URL"] = app.actions_url
    os.environ["TRACKER_STORE_TYPE"] = app.tracker_store_type
    os.environ["DB_HOST"] = app.database_host or ""
    os.environ["DB_PORT"] = app.database_port or ""
    os.environ["DB_NAME"] = app.database_name or ""
    os.environ["DB_USER"] = app.database_user or ""
    os.environ["DB_PASSWORD"] = app.database_password or ""
    os.environ["LOCK_STORE_TYPE"] = app.lock_store_type
    os.environ["REDIS_URL"] = app.redis_url or ""
    os.environ["REDIS_PORT"] = app.redis_port or ""
    os.environ["REDIS_DB"] = app.redis_db or ""


def main():
    global logger

    logger = logging.initialize_logging()

    logger.info("Starting Astro")

    app.log_config()
    set_endpoints_config_variables()

    if app.prometheus is True:
        start_prometheus()

    # Use API_PORT when set
    if app.api_port:
        sys.argv.extend(["--port", str(app.api_port)])

    rasa_main()


if __name__ == "__main__":
    main()
