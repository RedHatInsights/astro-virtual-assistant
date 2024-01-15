import signal
import sys

from prometheus_client import start_http_server
from threading import Event
from flask import Flask

from common import logging
from common.config import app


app = Flask(__name__)

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

    if app.prometheus is True:
        start_prometheus()

    # Use INTERNAL_PORT when set
    if app.internal_port:
        sys.argv.extend(["--port", str(app.internal_port)])

    logger.info("Starting virtual assistant internal api...")
    app.run(host=app.hostname, port=app.internal_port)


if __name__ == "__main__":
    main()
