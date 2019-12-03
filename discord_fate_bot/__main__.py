import environ
import logging
import os

from discord.ext.commands import Bot

from discord_fate_bot import config

bot_config = environ.to_config(config.BotConfig, os.environ)

if bot_config.log_level is not None:
    logging.basicConfig(level=bot_config.log_level)

logger = logging.getLogger('discord_fate_bot')

bot = Bot(command_prefix = '!')
bot.load_extension('discord_fate_bot.roll_ext')

bot.run(bot_config.token)

