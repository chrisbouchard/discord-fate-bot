import re

from discord.ext.commands import BadArgument, Cog, Converter, command
from typing import Optional

from ..dice import FateDiePool

DICE_POOL = FateDiePool()
MODIFIER_REGEX = re.compile(r'[+-]\d+')

class Modifier(Converter):
    """A positive or negative roll modifier."""
    async def convert(self, ctx, argument):
        if not MODIFIER_REGEX.fullmatch(argument):
            raise BadArgument("Modifier must have format: {+|-}VALUE")
        return int(argument)


class RollCog(Cog, name = 'Rolling'):
    """Commands for rolling dice."""

    @command(aliases = ['r'])
    async def roll(self, ctx, modifier: Modifier = 0):
        """Roll with an optional modifier."""
        player = ctx.author
        original_command = ctx.message.content

        roll = DICE_POOL.roll()
        shifts = roll.total() + modifier

        results_header = f'{player.mention} Results for `{original_command}`:\n'
        results_roll = f'```\n{roll}```\n'
        results_final = f'You generated **{shifts:+}** shifts.'

        await ctx.send(f'{results_header}{results_roll}{results_final}')

    @command(aliases = ['rv'])
    async def rollvs(self, ctx, modifier: Optional[Modifier] = 0, opposition: int = 0):
        """Roll against static opposition."""
        player = ctx.author
        original_command = ctx.message.content

        roll = DICE_POOL.roll()
        shifts = roll.total() + modifier - opposition

        results_header = f'{player.mention} Results for `{original_command}`:\n'
        results_roll = f'```\n{roll}```\n'

        if shifts >= 3:
            results_final = f'You **succeeded with style** with **{shifts:+}** shifts!'
        elif shifts > 0:
            results_final = f'You **succeeded** with **{shifts:+}** shifts.'
        elif shifts < 0:
            results_final = f'You **failed** with **{shifts:+}** shifts.'
        else:
            results_final = "You **tied**."

        await ctx.send(f'{results_header}{results_roll}{results_final}')


def setup(bot):
    bot.add_cog(RollCog())

