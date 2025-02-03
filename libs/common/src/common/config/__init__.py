import os

from collections import ChainMap
from decouple import Config, RepositoryEnv

from common.config.repository_clowdapp import RepositoryClowdapp
from common.config.repository_openshift import RepositoryOpenshift

__repository_chain = [os.environ]

__DOT_ENV_FILE = os.getenv("__DOT_ENV_FILE", ".env")

if os.path.exists(__DOT_ENV_FILE):
    print("Loading from .env file: %s" % __DOT_ENV_FILE)
    __repository_chain.append(RepositoryEnv(__DOT_ENV_FILE))

if os.getenv("ACG_CONFIG"):
    print("Loading clowdapp config from %s" % os.getenv("ACG_CONFIG"))
    from app_common_python import LoadedConfig

    __repository_chain.append(RepositoryClowdapp(LoadedConfig))

__repository_chain.append(RepositoryOpenshift())

config = Config(ChainMap(*__repository_chain))


def log_config(module, logging_function=None):
    if logging_function is None:
        import logging

        logging_function = logging.info

    primitives = (bool, str, int, float, type(None))

    def is_primitive(obj):
        return isinstance(obj, primitives)

    def should_log(key, value) -> bool:
        if not is_primitive(value):
            return False

        if key.startswith("_"):
            return False

        return True

    def get_value(key: str, value) -> str:
        if value is None or (
            isinstance(value, int) and not isinstance(value, bool) and value == 0
        ):
            return f"--not-set-- ({value})"

        upper_key = key.upper()
        accepted_variables = ["dev_sso_refresh_token_url"]
        if (
            any(
                banned in upper_key for banned in ["PASSWORD", "TOKEN", "SECRET", "KEY"]
            )
            and key not in accepted_variables
        ):
            return "*********"

        return str(value)

    for k, v in module.__dict__.items():
        if should_log(k, v):
            logging_function(f"Using {k}: {get_value(k, v)}")


# We could implement expanvars If we need variable expansion
# https://github.com/sayanarijit/expandvars
