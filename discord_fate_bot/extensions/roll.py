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
            vs: OppositionSigil = None,
            opposition: Opposition = None):
        """Roll with an optional modifier and opposition."""
        player = ctx.author

        context = RollContext(
            modifiers = tuple(modifiers),
            opposition = opposition
        )

        roll = DICE_POOL.roll(context)

        message = f'{player.mention} \[{ctx.message.content}\] {roll.description()}\n'
        message += f'```\n{roll.dice_display()}```\n'
        message += f'{roll.explanation()}'

        await ctx.send(message)


def setup(bot):
    bot.add_cog(RollCog())

