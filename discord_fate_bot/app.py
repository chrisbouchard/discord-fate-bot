import logging

from dataclasses import dataclass, field
from discord.ext.commands import Bot
from importlib.util import resolve_name

from .config import BotConfig, Config, LogConfig

_BOT_EXTENSIONS = [
    '.extensions.error_handling',
    '.extensions.lifecycle',
    '.extensions.aspect',
    '.extensions.roll'
]

@dataclass
class DiscordFateBotApp:
    config: Config = field(default_factory = Config.from_environ)

    def run(self):
        if self.config.log.level is not None:
            logging.basicConfig(level = self.config.log.level)

        bot = Bot(command_prefix = '!')

        for extension in _BOT_EXTENSIONS:
            # The load_extension method expects an "absolute" package name, but
            # we want to be relative because why not? So we resolve the name
            # relative to our package name.
            bot.load_extension(resolve_name(extension, __package__))

        bot.run(self.config.bot.read_token())

