import logging
from logging import Formatter

from logstash_formatter import LogstashFormatterV1
from .config import shared_config as app


class VirtualAssistantLogFormatter(Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(
            "%(asctime)s %(threadName)s %(levelname)s %(name)s - %(message)s"
        )

    def format(self, record):
        return super().format(record)


def build_logger(logger_type: str) -> None:
    if logger_type == "cloudwatch":
        _build_cloudwatch_logger()
    elif logger_type == "basic":
        _build_default_logger()
    else:
        raise NotImplementedError(f"The logger {logger_type} is not implemented.")


def _build_cloudwatch_logger() -> None:
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

def _build_default_logger() -> None:
    logging.basicConfig(level=logging.INFO)
