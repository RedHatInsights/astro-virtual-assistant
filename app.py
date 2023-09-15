import json
import signal
from functools import partial
from uuid import uuid4

import attr
from confluent_kafka import KafkaError
from prometheus_client import start_http_server
from threading import Event
from src.storage_broker import TrackerMessage, normalizers
from src.storage_broker.mq import consume, produce, msgs
from src.storage_broker.storage import aws
from src.storage_broker.utils import broker_logging, config, metrics

logger = broker_logging.initialize_logging()

event = Event()


def start_prometheus():
    start_http_server(config.PROMETHEUS_PORT)

def handle_signal(signal, frame):
    event.set()

signal.signal(signal.SIGTERM, handle_signal)

def main():

    logger.info("Starting Storage Broker")

    config.log_config()

    if config.PROMETHEUS == "True":
        start_prometheus()

if __name__ == "__main__":
    main()
