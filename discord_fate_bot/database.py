from contextlib import asynccontextmanager
from databases import Database
from discord.ext.commands import Bot, Cog

@asynccontextmanager
async def connect_database(bot: Bot):
    config_cog = bot.get_cog('Config')
    config = config_cog.config

    async with Database(config.database.url) as database:
        bot.add_cog(DatabaseCog(database))
        try:
            yield bot
        finally:
            bot.remove_cog('Database')


class DatabaseCog(Cog, name = 'Database'):
    database: Database

    def __init__(self, database: Database):
        self.database = database

