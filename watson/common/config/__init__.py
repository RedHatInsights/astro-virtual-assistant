import os

from collections import ChainMap
from decouple import Config

__repository_chain = [os.environ]


config = Config(ChainMap(*__repository_chain))
