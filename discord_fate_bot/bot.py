from discord.ext.commands import Bot, Cog
from importlib.util import resolve_name

from .config import Config

_BOT_EXTENSIONS = [
    '.extensions.error_handling',
    '.extensions.log_invite_url',
    '.extensions.aspects',
    '.extensions.rolling'
]

def make_bot(config: Config) -> Bot:
    bot = Bot(command_prefix = '!')

    bot.add_cog(ConfigCog(config))

    for extension in _BOT_EXTENSIONS:
        # The load_extension method expects an "absolute" package name, but we
        # want to be relative because why not? So we resolve the name relative
        # to our package name.
        bot.load_extension(resolve_name(extension, __package__))

    return bot

async def run_bot(bot: Bot):
    config_cog = bot.get_cog('Config')
    config = config_cog.config
    token = await config.bot.read_token()

    # This code is based on the documentation for Bot.run, except it has been
    # adapted to run *inside* the asyncio loop (so there's no need -- or
    # ability -- to close the loop).
    try:
        await bot.start(token)
    finally:
        await bot.logout()


class ConfigCog(Cog, name = 'Config'):
    config: Config

    def __init__(self, config: Config):
        self.config = config

