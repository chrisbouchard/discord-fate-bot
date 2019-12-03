import re

from discord.ext import commands
from typing import Optional

from discord_fate_bot.dice import FateDiePool

DICE_POOL = FateDiePool()
MODIFIER_REGEX = re.compile(r'[+-]\d+')

class Modifier(commands.Converter):
    async def convert(self, ctx, argument):
        if not MODIFIER_REGEX.fullmatch(argument):
            raise commands.CommandError("Modifier must have format: {+|-}VALUE")
        return int(argument)

@commands.command(aliases=['r'])
async def roll(ctx, modifier: Modifier = 0):
    roll = DICE_POOL.roll()
    shifts = roll.total() + modifier

    reply = ctx.message.author.mention
    original_command = ctx.message.content

    await ctx.send(f'{reply} Results for `{original_command}`:\n```\n{roll}```\nGenerated **{shifts:+}** shifts')


def setup(bot):
    bot.add_command(roll)

