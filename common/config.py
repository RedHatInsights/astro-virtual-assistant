import os
import logging

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

LOCK_STORE_TYPE = os.getenv("LOCK_STORE_TYPE", "redis")


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

    for k in [
        "ENDPOINT_ADVISOR_BACKEND",
        "ENDPOINT_NOTIFICATIONS_GW",
        "ENDPOINT_VULNERABILITY_ENGINE",
    ]:
        logger.info("Using %s: %s", k, os.environ.get(k, "--not-set--"))


def get_namespace():
    try:
        with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r") as f:
            namespace = f.read()
        return namespace
    except EnvironmentError:
        logger.info("Not running in openshift")


def get_endpoint_url(endpoint):
    # TODO: need to check if tlsPort is present, if so use https (and configure certs)
    return "http://%s:%s" % (endpoint.hostname, endpoint.port)


if os.getenv("ACG_CONFIG"):
    from app_common_python import LoadedConfig, DependencyEndpoints

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
    ACTIONS_PORT = int(os.getenv("ACTIONS_PORT", cfg.privatePort))

    # Postgres Database
    os.environ["DB_HOST"] = cfg.database.hostname
    os.environ["DB_PORT"] = str(cfg.database.port)
    os.environ["DB_USER"] = cfg.database.username
    os.environ["DB_PASSWORD"] = cfg.database.password
    os.environ["DB_NAME"] = cfg.database.name
    os.environ["DB_SSLMODE"] = cfg.database.sslMode

    # Redis
    try:
        os.environ["REDIS_URL"] = cfg.InMemoryDb.Hostname
        os.environ["REDIS_PORT"] = cfg.InMemoryDb.Port
    except Exception:
        logger.info("No redis config found")
        os.environ["LOCK_STORE_TYPE"] = "in_memory"
        os.environ["REDIS_URL"] = ""
        os.environ["REDIS_PORT"] = ""
        os.environ["REDIS_DB"] = ""

    # Endpoints
    os.environ["ENDPOINT_ADVISOR_BACKEND"] = get_endpoint_url(
        DependencyEndpoints.get("advisor-backend").get("api")
    )
    os.environ["ENDPOINT_NOTIFICATIONS_GW"] = get_endpoint_url(
        DependencyEndpoints.get("notifications-gw").get("service")
    )
    os.environ["ENDPOINT_VULNERABILITY_ENGINE"] = get_endpoint_url(
        DependencyEndpoints.get("vulnerability-engine").get("manager-service")
    )

else:
    # Logging
    CW_AWS_ACCESS_KEY_ID = os.getenv("CW_AWS_ACCESS_KEY_ID", None)
    CW_AWS_SECRET_ACCESS_KEY = os.getenv("CW_AWS_SECRET_ACCESS_KEY", None)
    LOG_GROUP = os.getenv("LOG_GROUP", "platform-dev")

    # Metrics
    PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_PORT", 9000))

    API_PORT = int(os.getenv("API_PORT")) if os.getenv("API_PORT") else None
    ACTIONS_PORT = int(os.getenv("ACTIONS_PORT")) if os.getenv("ACTIONS_PORT") else None
