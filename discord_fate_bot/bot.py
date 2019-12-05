from discord.ext.commands import Bot
from importlib.util import resolve_name

def create_bot():
    bot = Bot(command_prefix = '!')
    bot.load_extension(resolve_name('.extensions.error_handling', __package__))
    bot.load_extension(resolve_name('.extensions.aspect', __package__))
    bot.load_extension(resolve_name('.extensions.roll', __package__))
    return bot

