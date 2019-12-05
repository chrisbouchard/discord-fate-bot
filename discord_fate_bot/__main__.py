import environ
import logging
import os

from .bot import create_bot
from .model.config import Config

config = environ.to_config(Config, os.environ)

if config.log_level is not None:
    logging.basicConfig(level = config.log_level)

bot = create_bot()
bot.run(config.token)

