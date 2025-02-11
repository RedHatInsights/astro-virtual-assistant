from decouple import undefined as __undefined, Choices
from . import config
import os

is_running_locally = config("IS_RUNNING_LOCALLY", default=False, cast=bool)
__optional_when_locally = __undefined if is_running_locally is False else None

## aws/logs configuration
aws_region = config("AWS_REGION", default="us-east-1")
log_level = config(
    "LOG_LEVEL",
    default="INFO",
    cast=Choices(["CRITICAL", "FATAL", "ERROR", "WARN", "INFO", "DEBUG"]),
)
namespace = config("NAMESPACE", default=None)
hostname = config("HOSTNAME", default=None)
prometheus = config("PROMETHEUS", default=False, cast=bool)
prometheus_port = config("METRICS_PORT", default=0, cast=int)

logging_cloudwatch_access_key_id = config(
    "LOGGING_CLOUDWATCH_ACCESS_KEY_ID", default=__optional_when_locally
)
logging_cloudwatch_secret_access_key = config(
    "LOGGING_CLOUDWATCH_SECRET_ACCESS_KEY", default=__optional_when_locally
)
logging_cloudwatch_region = config(
    "LOGGING_CLOUDWATCH_REGION", default=__optional_when_locally
)
logging_cloudwatch_log_group = config(
    "LOGGING_CLOUDWATCH_LOG_GROUP", default=__optional_when_locally
)
logging_cloudwatch_create_log_group = config(
    "AWS_CREATE_LOG_GROUP", default=True, cast=bool
)
logging_cloudwatch_log_stream = config("AWS_LOG_STREAM", default=os.uname().nodename)
