import asyncio
import logging

from .bot import make_bot, run_bot
from .config import Config
from .database import connect_database

async def main():
    config = Config.from_environ()

    if config.log.level is not None:
        logging.basicConfig(level = config.log.level)

    bot = make_bot(config)

    async with connect_database(bot):
        await run_bot(bot)

asyncio.run(main())

