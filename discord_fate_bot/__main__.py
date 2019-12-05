import environ

from . import bot, config, logging

config = config.read()

logging.setup(config.log)
bot.run(config.bot)

