import environ
import logging
import os

from discord.ext.commands import Bot
from importlib.util import resolve_name

from .model.config import Config

config = environ.to_config(Config, os.environ)

if config.log_level is not None:
    logging.basicConfig(level = config.log_level)

bot = Bot(command_prefix = '!')
bot.load_extension(resolve_name('.extensions.error_handling', __package__))
bot.load_extension(resolve_name('.extensions.aspect', __package__))
bot.load_extension(resolve_name('.extensions.roll', __package__))

bot.run(config.token)

