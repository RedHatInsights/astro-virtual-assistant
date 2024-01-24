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
    if LoadedConfig.database.rdsCa is not None:
        LoadedConfig.rds_ca()

    if (
        len(LoadedConfig.kafka.brokers) > 0
        and LoadedConfig.kafka.brokers[0].cacert is not None
    ):
        LoadedConfig.kafka_ca()

__repository_chain.append(RepositoryOpenshift())

config = Config(ChainMap(*__repository_chain))

# We could implement expanvars If we need variable expansion
# https://github.com/sayanarijit/expandvars
