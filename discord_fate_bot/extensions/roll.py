import asyncio
import re

from discord.ext.commands import BadArgument, Cog, Converter, Greedy, command
from typing import Optional

from ..dice import FateDiePool, Roll, RollContext, Value

DICE_POOL = FateDiePool()

class Modifier(Converter):
    """A positive or negative roll modifier."""
    async def convert(self, ctx, argument):
        if argument[:1] not in ('+', '-'):
            raise BadArgument("Modifier must have format: {+|-}VALUE")
        try:
            return Value(int(argument))
        except ValueError:
            raise BadArgument("Modifier must be numeric")

class Opposition(Converter):
    """A numeric value."""
    async def convert(self, ctx, argument):
        try:
            return Value(int(argument))
        except ValueError:
            raise BadArgument("Opposition must be numeric")

class OppositionSigil(Converter):
    """A separator."""
    async def convert(self, ctx, argument):
        if argument != 'vs':
            raise BadArgument("Opposition must be numeric")
        return None


class RollCog(Cog, name = 'Rolling'):
    """Commands for rolling dice."""

    @command(aliases = ['r'])
    async def roll(
            self, ctx,
            modifiers: Greedy[Modifier],
            vs: Optional[OppositionSigil],
            opposition: Optional[Opposition]):
        """Roll with an optional modifier and opposition."""
        player = ctx.author

        context = RollContext(
            modifiers = tuple(modifiers),
            opposition = opposition
        )

        roll = DICE_POOL.roll(context)

        results_header = f'{player.mention} Results for roll:'
        results_roll = f'```\n{roll}```'
        results_final = format_roll_result(roll)

        await ctx.send(f'{results_header}\n{results_roll}\n{results_final}')


def format_roll_result(roll: Roll):
    shifts = roll.result()

    if shifts >= 3:
        return f'You **succeeded with style** with **{shifts}** shifts!'
    elif shifts > 0:
        return f'You **succeeded** with **{shifts}** shifts.'
    elif shifts < 0:
        return f'You **failed** with **{shifts}** shifts.'
    else:
        return "You **tied**."

def setup(bot):
    bot.add_cog(RollCog())

