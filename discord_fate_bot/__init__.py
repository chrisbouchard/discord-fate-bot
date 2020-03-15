import environ

from . import bot, config, logging

def run():
    c = config.read()

    logging.setup(c.log)
    bot.run(c.bot)

