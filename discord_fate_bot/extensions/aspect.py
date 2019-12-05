from discord.ext.commands import Cog, command, group
from discord.utils import escape_markdown, find
from typing import Dict, List, Optional, Union

class AspectsCog(Cog, name = 'Aspects'):
    """Commands for managing aspects on the scene."""
    aspects: Dict[int, List[str]]

    def __init__(self):
        self.aspects = dict()

    @group()
    async def aspect(self, ctx):
        """Manage the aspects on the scene."""
        pass

    @aspect.command()
    async def list(self, ctx):
        """List the aspects on the scene."""
        channel_id = ctx.channel.id
        aspects = self.aspects.get(channel_id)
        await self.send_aspects(ctx, aspects)

    @aspect.command()
    async def add(self, ctx, *, description: str):
        """Add an aspect to the scene."""
        channel_id = ctx.channel.id
        safe_description = escape_markdown(description)

        aspects = self.aspects.setdefault(channel_id, [])
        new_aspect_index = len(aspects)
        aspects.append(safe_description)

        await self.send_aspects(ctx, aspects, highlight_index = new_aspect_index)

    @aspect.command()
    async def remove(self, ctx, position: int):
        """Remove an aspect from the scene."""
        channel_id = ctx.channel.id
        aspects = self.aspects.get(channel_id, [])

        index = position - 1

        if 0 <= index < len(aspects):
            del aspects[index]
            await self.send_aspects(ctx, aspects)
        else:
            player = ctx.author
            await ctx.send(f"{player.mention} There's no aspect #{position} in this scene")

    @aspect.command()
    async def clear(self, ctx):
        """Remove all aspects from the scene."""
        channel_id = ctx.channel.id

        if channel_id in self.aspects:
            del self.aspects[channel_id]

        await ctx.send('_Cleared all aspects._')

    async def send_aspects(self, ctx, aspects, *, highlight_index = None, title = 'Current Aspects'):
        if not aspects:
            listing = 'There are no aspects on this scene.'
        else:
            listing = ''

            for (i, aspect) in enumerate(aspects):
                bold = '**' if i == highlight_index else ''
                newline = '\n' if i != 0 else ''
                listing += f'{newline}{bold}{i + 1}. {aspect}{bold}'

        return await ctx.send(f'**__{title}__:**\n{listing}')


def setup(bot):
    bot.add_cog(AspectsCog())

