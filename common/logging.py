import sys
import logging
from logging import Formatter

from logstash_formatter import LogstashFormatterV1
from .config import app


class VirtualAssistantLogFormatter(Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__("%(asctime)s %(threadName)s %(levelname)s %(name)s - %(message)s")

    def format(self, record):
            return super().format(record)


_app_logger = None


def initialize_logging():
    global _app_logger
    if _app_logger is None:
        # Configure logs before Rasa takes over
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(VirtualAssistantLogFormatter())
        logging.root.setLevel(app.log_level)
        logging.root.addHandler(handler)

        if all(
            (
                app.logging_cloudwatch_access_key_id,
                app.logging_cloudwatch_secret_access_key,
                app.logging_cloudwatch_region,
                app.logging_cloudwatch_log_group,
            )
        ):
            from boto3.session import Session
            import watchtower

            boto3_session = Session(
                aws_access_key_id=app.logging_cloudwatch_access_key_id,
                aws_secret_access_key=app.logging_cloudwatch_secret_access_key,
                region_name=app.logging_cloudwatch_region,
            )
            boto3_client = boto3_session.client("logs")

            cw_handler = watchtower.CloudWatchLogHandler(
                boto3_client=boto3_client,
                log_group_name=app.logging_cloudwatch_log_group,
                log_stream_name=app.logging_cloudwatch_log_stream,
                create_log_group=app.logging_cloudwatch_create_log_group,
            )

            cw_handler.setFormatter(LogstashFormatterV1())
            logging.root.addHandler(cw_handler)

        _app_logger = logging.getLogger(app.name)

    return _app_logger
