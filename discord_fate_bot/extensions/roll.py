import re

from dataclasses import dataclass
from discord import Member, TextChannel
from discord.abc import User
from discord.ext.commands import BadArgument, Cog, Converter, command
from typing import Dict, FrozenSet, Optional, OrderedDict

from ..dice import FateDiePool, Roll, RollContext

DICE_POOL = FateDiePool()
MODIFIER_REGEX = re.compile(r'[+-]\d+')

class Modifier(Converter):
    """A positive or negative roll modifier."""
    async def convert(self, ctx, argument):
        if not MODIFIER_REGEX.fullmatch(argument):
            raise BadArgument("Modifier must have format: {+|-}VALUE")
        return int(argument)


@dataclass(frozen = True)
class PendingVsKey:
    channel_id: TextChannel
    user_ids: FrozenSet[User]

PendingVs = OrderedDict[User, RollContext]


class RollCog(Cog, name = 'Rolling'):
    """Commands for rolling dice."""

    pending_vs: Dict[PendingVsKey, PendingVs]

    def __init__(self):
        self.pending_vs = dict()

    @command(aliases = ['r'])
    async def roll(self, ctx, modifier: Optional[Modifier] = None, opposition: int = None):
        """Roll with an optional modifier and opposition."""
        player = ctx.author

        context = RollContext(
            modifiers = (modifier, ) if modifier else (),
            opposition = opposition
        )

        roll = DICE_POOL.roll(context)

        results_header = f'{player.mention} Results for roll:'
        results_roll = f'```\n{roll}```'
        results_final = format_roll_result(roll)

        await ctx.send(f'{results_header}\n{results_roll}\n{results_final}')

    @command(aliases = ['rv'])
    async def rollvs(self, ctx, opponent: User, modifier: Modifier = None):
        """Roll against another user."""
        channel = ctx.channel
        author = ctx.author

        if author == opponent:
            await ctx.send(f"{author.mention} You can't roll against yourself.")
            return

        pending_vs_key = PendingVsKey(
            channel_id = channel,
            user_ids = frozenset({author, opponent})
        )

        pending_vs = self.pending_vs.setdefault(pending_vs_key, OrderedDict())

        context = RollContext(
            modifiers = (modifier, ) if modifier else ()
        )

        pending_vs[author] = context

        # If our opponent is not ready, we'll get them later.
        if opponent not in pending_vs:
            return

        del self.pending_vs[pending_vs_key]

        rolls = {
            user: DICE_POOL.roll(context)
            for user, context in pending_vs.items()
        }

        results_header = f'Results for opposed roll:'
        results_roll = '\n'.join(f'{user.mention}:\n```{roll}```' for user, roll in rolls.items())
        results_final = format_opposed_roll_result(rolls)

        await ctx.send(f'{results_header}\n\n{results_roll}\n{results_final}')


def format_roll_result(roll: Roll):
    shifts = roll.result()

    if roll.context.is_opposed():
        return f'You generated **{shifts:+}** shifts.'

    if shifts >= 3:
        return f'You **succeeded with style** with **{shifts:+}** shifts!'
    elif shifts > 0:
        return f'You **succeeded** with **{shifts:+}** shifts.'
    elif shifts < 0:
        return f'You **failed** with **{shifts:+}** shifts.'
    else:
        return "You **tied**."

def format_opposed_roll_result(rolls: Dict[User, Roll]):
    loser, winner = sorted(rolls.keys(), key = lambda user: rolls[user].result())
    shifts = rolls[winner].result() - rolls[loser].result()

    if shifts > 0:
        return f'{winner.mention} **won** by **{shifts}** shifts.'
    else:
        return f'{winner.mention} and {loser.mention} **tied**.'

def setup(bot):
    bot.add_cog(RollCog())

