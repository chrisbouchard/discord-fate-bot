import asyncio
import re

from collections import defaultdict
from dataclasses import dataclass
from discord import Member, TextChannel
from discord.abc import User
from discord.ext.commands import BadArgument, Cog, Converter, command, group
from typing import Dict, FrozenSet, Optional, Tuple

from ..dice import FateDiePool, Roll, RollContext

DICE_POOL = FateDiePool()
MODIFIER_REGEX = re.compile(r'[+-]\d+')

class Modifier(Converter):
    """A positive or negative roll modifier."""
    async def convert(self, ctx, argument):
        if not MODIFIER_REGEX.fullmatch(argument):
            raise BadArgument("Modifier must have format: {+|-}VALUE")
        return int(argument)


class PendingVs:
    waiting: Dict[Tuple[TextChannel, User], Dict[User, RollContext]]

    def __init__(self):
        self.waiting = defaultdict(dict)

    def add_context(self, channel: TextChannel, player: User, opponent: User, context: RollContext):
        key = (channel, player)
        self.waiting[key][opponent] = context

    def remove_context(self, channel: TextChannel, player: User, opponent: User):
        key = (channel, player)

        if not key in self.waiting:
            return

        waiting_for_player = self.waiting[key]

        if opponent not in waiting_for_player:
            return

        del waiting_for_player[opponent]

        if not waiting_for_player:
            del self.waiting[key]

    def pop_opponent_context(self, channel: TextChannel, player: User, opponent: User):
        key = (channel, opponent)

        if key not in self.waiting:
            return None

        waiting_for_opponent = self.waiting[key]

        if player not in waiting_for_opponent:
            return None

        opponent_context = waiting_for_opponent.pop(player)

        if not waiting_for_opponent:
            del self.waiting[key]

        return opponent_context

    def get_all_pending(self, channel: TextChannel, player: User):
        key = (channel, player)

        if key not in self.waiting:
            return []

        return list(self.waiting[key].keys())


class RollCog(Cog, name = 'Rolling'):
    """Commands for rolling dice."""

    pending_vs: PendingVs
    vs_lock: asyncio.Lock

    def __init__(self):
        self.pending_vs = PendingVs()
        self.vs_lock = asyncio.Lock()

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

    @group(aliases = ['rv'], invoke_without_command = True)
    async def rollvs(self, ctx, opponent: Member, modifier: Modifier = None):
        """Roll against another user.

        Once both users have called this command, the rolls will be made."""
        channel = ctx.channel
        player = ctx.author

        if player == opponent:
            await ctx.send(f"{player.mention} You can't roll against yourself.")
            return

        player_context = RollContext(
            modifiers = (modifier, ) if modifier else ()
        )

        async with self.vs_lock:
            opponent_context = self.pending_vs.pop_opponent_context(channel, player, opponent)

            # If we're first, just add our context and bail.
            if not opponent_context:
                self.pending_vs.add_context(channel, player, opponent, player_context)
                return

        contexts = {
            player: player_context,
            opponent: opponent_context
        }

        rolls = {
            user: DICE_POOL.roll(context)
            for user, context in contexts.items()
        }

        results_header = f'Results for opposed roll:'
        results_roll = '\n'.join(f'{user.mention}:\n```{roll}```' for user, roll in rolls.items())
        results_final = format_opposed_roll_result(rolls)

        await ctx.send(f'{results_header}\n\n{results_roll}\n{results_final}')

    @rollvs.command()
    async def who(self, ctx):
        """List the users you have pending rolls against."""
        channel = ctx.channel
        player = ctx.author

        async with self.vs_lock:
            users = self.pending_vs.get_all_pending(channel, player)

        if not users:
            await ctx.send(f"{player.mention} You aren't waiting on any rolls.")
            return

        users_str = '\n'.join(f'    • {user.name}' for user in users)

        await ctx.send(f'{player.mention} You are waiting on rolls from:\n{users_str}')


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

