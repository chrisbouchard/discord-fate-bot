from discord.ext.commands import BadArgument, Cog, Converter, Greedy, command
from typing import Optional

from ..dice import FateDiePool, Roll, RollContext, Value
from ..emojis import ROLL_EMOJI

def setup(bot):
    bot.add_cog(RollingCog())

DICE_POOL = FateDiePool()

class Modifier(Converter):
    """A positive or negative roll modifier."""
    async def convert(self, ctx, argument):
        if argument[:1] not in ('+', '-'):
            raise BadArgument('A modifier must have format: {+|-}VALUE')
        try:
            return Value(int(argument))
        except ValueError:
            raise BadArgument('A modifier must be a number')

class Opposition(Converter):
    """A numeric value."""
    async def convert(self, ctx, argument):
        try:
            return Value(int(argument))
        except ValueError:
            raise BadArgument('Opposition must be a number')

class OppositionSigil(Converter):
    """A separator."""
    async def convert(self, ctx, argument):
        if argument != 'vs':
            raise BadArgument('Expected "vs"')
        return argument


class RollingCog(Cog, name = 'Rolling'):
    """Commands for rolling dice."""

    @command(aliases = ['r'], ignore_extra = False)
    async def roll(
            self, ctx,
            modifiers: Greedy[Modifier],
            vs: OppositionSigil = None,
            opposition: Opposition = None):
        """Roll with optional modifiers and opposition.

        MODIFIERS

          Zero or more modifiers may be given, each starting with a "+" or "-",
          e.g., "+3" or "-1".

        OPPOSITION

          At most one opposition may be given. If no opposition is given, the
          roll simply generates shifts vs 0. If opposition is given, the result
          will be either failure, success, or success with style.

        EXAMPLES

          !roll
              Roll with no modifier and no opposition.

          !roll +2
              Roll with a +2 modifier and no opposition.

          !roll +1 vs 3
              Roll with a +1 modifier and an opposition of 3.

          !roll -1 +2 vs 3
              Roll with a +1 modifier (−1 + +2) and an opposition of 3.
        """
        if vs is not None and opposition is None:
            raise BadArgument('Found "vs" but no opposition')

        player = ctx.author

        context = RollContext(
            modifiers = tuple(modifiers),
            opposition = opposition
        )

        roll = DICE_POOL.roll(context)

        message = f'{ROLL_EMOJI} {player.mention} \[{ctx.message.content}\]  {roll.description()}\n\n'
        message += f'```\n{roll.dice_display()}```\n'
        message += f'({roll.explanation()})'

        await ctx.send(message)

