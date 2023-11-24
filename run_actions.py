import signal
import sys

from prometheus_client import start_http_server
from threading import Event
from common import logging
from common.config import app

from rasa_sdk.__main__ import main as rasa_sdk_main

logger = None

event = Event()


def start_prometheus():
    start_http_server(app.prometheus_port)


def handle_signal(signal, frame):
    event.set()


signal.signal(signal.SIGTERM, handle_signal)


def main():
    global logger

    logger = logging.initialize_logging()
    logger.info("Starting Astro")
    app.log_config()

    if app.prometheus.PROMETHEUS is True:
        start_prometheus()

    # Use ACTIONS_PORT when set
    if app.actions_port:
        sys.argv.extend(["--port", str(app.actions_port)])

    rasa_sdk_main()


if __name__ == "__main__":
    main()
