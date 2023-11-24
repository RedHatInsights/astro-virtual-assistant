import sys
import logging
from logstash_formatter import LogstashFormatterV1
from .config import app


def initialize_logging():
    if app.namespace is not None:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(LogstashFormatterV1())
        logging.root.setLevel(app.log_level)
        logging.root.addHandler(handler)
    else:
        logging.basicConfig(
            level=app.log_level,
            format="%(threadName)s %(levelname)s %(name)s - %(message)s",
        )

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

    logger = logging.getLogger(app.name)

    return logger
