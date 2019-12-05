import logging

from .config import LogConfig

def setup(config: LogConfig):
    if config.level is not None:
        logging.basicConfig(level = config.level)

