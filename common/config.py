import os
import logging
import yaml

APP_NAME = os.getenv("APP_NAME", "astro-virtual-assistant")

logger = logging.getLogger(APP_NAME)

# define GROUP_ID, API_LISTEN_ADDRESS, API_URL_EXPIRY, AWS_REGION, LOG_LEVEL, NAMESPACE, HOSTNAME, PROMETHEUS
GROUP_ID = None
API_LISTEN_ADDRESS = None
API_URL_EXPIRY = None
AWS_REGION = None
LOG_LEVEL = None
NAMESPACE = None
HOSTNAME = None
PROMETHEUS = None

def initialize_clowdapp():
    global GROUP_ID, API_LISTEN_ADDRESS, API_URL_EXPIRY, AWS_REGION, LOG_LEVEL, NAMESPACE, HOSTNAME, PROMETHEUS
    GROUP_ID = os.getenv("GROUP_ID", APP_NAME)

    API_LISTEN_ADDRESS = os.getenv("API_LISTEN_ADDRESS", "0.0.0.0")
    API_URL_EXPIRY = int(os.getenv("API_URL_EXPIRY", 30))

    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    NAMESPACE = get_namespace()
    HOSTNAME = os.environ.get("HOSTNAME")

    PROMETHEUS = os.getenv("PROMETHEUS", "false")

def log_config():
    import sys

    for k, v in sys.modules[__name__].__dict__.items():
        if k == k.upper():
            if "AWS" in k.split("_"):
                continue
            logger.info("Using %s: %s", k, v)

def get_namespace():
    try:
        with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as f:
            namespace = f.read()
        return namespace
    except EnvironmentError:
        logger.info("Not running in openshift")

if os.getenv("ACG_CONFIG"):
    from app_common_python import LoadedConfig

    cfg = LoadedConfig
    # Logging
    CW_AWS_ACCESS_KEY_ID = os.getenv(
        "CW_AWS_ACCESS_KEY_ID", cfg.logging.cloudwatch.accessKeyId
    )
    CW_AWS_SECRET_ACCESS_KEY = os.getenv(
        "CW_AWS_SECRET_ACCESS_KEY", cfg.logging.cloudwatch.secretAccessKey
    )
    LOG_GROUP = os.getenv("LOG_GROUP", cfg.logging.cloudwatch.logGroup)
    # Metrics
    PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", cfg.metricsPort))
    API_PORT = int(os.getenv("API_PORT", cfg.publicPort))
else:
    # Logging
    CW_AWS_ACCESS_KEY_ID = os.getenv("CW_AWS_ACCESS_KEY_ID", None)
    CW_AWS_SECRET_ACCESS_KEY = os.getenv("CW_AWS_SECRET_ACCESS_KEY", None)
    LOG_GROUP = os.getenv("LOG_GROUP", "platform-dev")
    # Metrics
    PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", 9000))
    API_PORT = int(os.getenv("API_PORT", 5005))
