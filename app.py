import signal

from prometheus_client import start_http_server
from threading import Event
from common import logging, config

logger = logging.initialize_logging()

event = Event()

def start_prometheus():
    start_http_server(config.PROMETHEUS_PORT)

def handle_signal(signal, frame):
    event.set()

signal.signal(signal.SIGTERM, handle_signal)

def main():

    logger.info("Starting Astro")

    config.log_config()

    if config.PROMETHEUS == "True":
        start_prometheus()

if __name__ == "__main__":
    main()
