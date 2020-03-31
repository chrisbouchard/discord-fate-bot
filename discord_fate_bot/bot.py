from discord.ext.commands import Bot, Cog
from importlib.util import resolve_name
from motor.motor_asyncio import AsyncIOMotorDatabase

from .config import Config

_BOT_EXTENSIONS = [
    '.extensions.error_handling',
    '.extensions.log_invite_url',
    '.extensions.rolling',
    '.extensions.scene_management',
]

class DiscordFateBot(Bot):
    config: Config
    database: AsyncIOMotorDatabase

    def __init__(self, config, database):
        super().__init__(command_prefix = '!')

        self.config = config
        self.database = database

        for extension in _BOT_EXTENSIONS:
            # The load_extension method expects an "absolute" package name, but we
            # want to be relative because why not? So we resolve the name relative
            # to our package name.
            self.load_extension(resolve_name(extension, __package__))

    async def run(self):
        token = await self.config.bot.read_token()

        # This code is based on the documentation for Bot.run, except it has been
        # adapted to run *inside* the asyncio loop (so there's no need -- or
        # ability -- to close the loop).
        try:
            await self.start(token)
        finally:
            await self.logout()

