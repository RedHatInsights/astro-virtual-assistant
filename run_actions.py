import signal
import sys

from prometheus_client import start_http_server
from threading import Event
from common import logging, config

from rasa_sdk.__main__ import main as rasa_sdk_main

logger = None

event = Event()


def start_prometheus():
    start_http_server(config.PROMETHEUS_PORT)


def handle_signal(signal, frame):
    event.set()


signal.signal(signal.SIGTERM, handle_signal)


def main():
    global logger

    config.initialize_clowdapp()
    logger = logging.initialize_logging()

    logger.info("Starting Astro")

    config.log_config()

    if config.PROMETHEUS == "True":
        start_prometheus()

    # Use ACTIONS_PORT when set
    if config.ACTIONS_PORT:
        sys.argv.extend(["--port", str(config.ACTIONS_PORT)])

    rasa_sdk_main()


if __name__ == "__main__":
    main()
