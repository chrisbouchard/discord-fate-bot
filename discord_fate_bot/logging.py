import logging

from .model.config import LogConfig

def setup(config: LogConfig):
    if config.level is not None:
        logging.basicConfig(level = config.level)

