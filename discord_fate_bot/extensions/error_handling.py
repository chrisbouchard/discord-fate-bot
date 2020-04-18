import logging
import textwrap

from discord.ext.commands import (
    CheckFailure, Cog, CommandNotFound, CommandInvokeError, UserInputError
)

from ..emojis import random_error_emoji
from ..scenes import AspectIdError, NoCurrentSceneError
from ..util import ValidationError

logger = logging.getLogger(__name__)

def setup(bot):
    bot.add_cog(ErrorHandlingCog())


class ErrorHandlingCog(Cog):
    @Cog.listener()
    async def on_command_error(self, ctx, error):
        try:
            original_error = error

            # Commands wrap their exceptions with this one.
            if isinstance(error, CommandInvokeError):
                error = error.__cause__

            if isinstance(error, AspectIdError):
                message = (
                    f"Sorry, there's no aspect in the current scene with id " \
                    f"{error.aspect_id}."
                )
                await send_error_message(ctx, message)
            elif isinstance(error, CommandNotFound) or isinstance(error, UserInputError):
                message = (
                    f"Sorry, I didn't understand:\n\n" \
                    f"{quote(ctx.message)}\n\n" \
                    f"{punctuate(error)}"
                )
                await send_error_message(ctx, message, help_separator=' ')
            elif isinstance(error, CheckFailure):
                message = (
                    f"Sorry, that command cannot be used right now. {punctuate(error)}"
                )
                await send_error_message(ctx, message)
            elif isinstance(error, NoCurrentSceneError):
                message = (
                    f"Sorry, there's no current scene in this channel. You can " \
                    f"start a new scene using **!scene new**."
                )
                await send_error_message(ctx, message)
            elif isinstance(error, ValidationError):
                message = f"{error}:\n\n"
                message += '\n'.join(
                    f'    •  {complaint}'
                    for complaint in error.complaints
                )
                await send_error_message(ctx, message)
            else:
                message = f"Sorry, something unexpected went wrong."
                await send_error_message(ctx, message)
                raise original_error
        except Exception as ex:
            # This whole method is basically a catch clause, but we don't get
            # implicit exception chaining. So let's just add our own explicit
            # chaining.
            if ex == original_error:
                # Don't try to chain the exception to itself. This gives us an
                # escape hatch if we need to re-raise the exception.
                raise original_error
            raise ex from original_error

async def send_error_message(ctx, message, *, help_separator='\n\n'):
    """Send an error message with our standard boilerplate."""
    emoji = random_error_emoji()

    if ctx.command:
        help_command = '!help ' + ctx.command.qualified_name
    else:
        help_command = '!help'

    if ctx.guild:
        mention = f"{ctx.author.mention} "
        dm_offer = f"(Feel free to DM that to {ctx.me.mention}.)"
    else:
        mention = ""
        dm_offer = ""

    final_message = (
        f"{emoji}  {mention}{message}{help_separator}" \
        f"Try **{help_command}** for more information. {dm_offer}"
    )
    await ctx.send(content=final_message)

def quote(message):
    content = message.content
    return textwrap.indent(content, '> ', lambda line: True)

def punctuate(text):
    text = str(text)
    if text[-1] in '!?.':
        return text
    return f"{text}."

