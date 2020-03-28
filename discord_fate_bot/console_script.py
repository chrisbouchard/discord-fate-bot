import aiorun
import logging

from .bot import make_bot, run_bot
from .config import Config
from .logging import configure_logging

logger = logging.getLogger(__name__)

def main():
    config = Config.from_environ()
    configure_logging(config)

    logger.info('Starting bot...')

    async def _main():
        bot = make_bot(config)
        await run_bot(bot)

    aiorun.run(_main(), stop_on_unhandled_errors=True)

