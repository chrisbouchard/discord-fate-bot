import importlib.resources
import logging
import logging.config

from .config import Config

logger = logging.getLogger(__name__)

def configure_logging(config: Config):
    # Always start by applying our base log configuration.
    with importlib.resources.path('discord_fate_bot', 'logging.ini') as path:
        logging.config.fileConfig(path, disable_existing_loggers=False)

    config_file = config.log.config_file

    # Then, if the user has supplied any, apply theirs.
    if config_file is not None:
        logging.config.fileConfig(config_file, disable_existing_loggers=False)
        logger.info( 'Logging configuration read from %s', config_file)

