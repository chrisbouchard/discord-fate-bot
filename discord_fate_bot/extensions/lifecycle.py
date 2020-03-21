import logging

from discord import Permissions
from discord.ext.commands import Cog
from discord.utils import oauth_url

def setup(bot):
    bot.add_cog(LifecycleCog(bot))

logger = logging.getLogger(__name__)

class LifecycleCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_connect(self):
        permissions = Permissions(
            add_reactions = True,
            manage_messages = True,
            read_message_history = True,
            read_messages = True,
            send_messages = True,
        )

        url = oauth_url(self.bot.user.id, permissions)

        logger.info('Invite URL: %s', url)

