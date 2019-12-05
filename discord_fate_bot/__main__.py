import environ

from . import bot, logging
from .model import config

config = config.read()

logging.setup(config.log)
bot.run(config.bot)

