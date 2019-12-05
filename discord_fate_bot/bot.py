from discord.ext.commands import Bot
from importlib.util import resolve_name

from .model.config import BotConfig

def run(config: BotConfig):
    bot = Bot(command_prefix = '!')

    bot.load_extension(resolve_name('.extensions.error_handling', __package__))
    bot.load_extension(resolve_name('.extensions.aspect', __package__))
    bot.load_extension(resolve_name('.extensions.roll', __package__))

    bot.run(config.token)

