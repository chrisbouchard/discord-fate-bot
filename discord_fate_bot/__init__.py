import aiorun
import logging

from .bot import make_bot, run_bot
from .config import Config
from .database import connect_database

logger = logging.getLogger(__name__)

def main():
    async def _main():
        config = Config.from_environ()
        config.log.apply_global()

        bot = make_bot(config)

        async with connect_database(bot):
            await run_bot(bot)

    aiorun.run(_main(), stop_on_unhandled_errors=True)

