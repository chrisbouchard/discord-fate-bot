import logging
import random
import textwrap

from discord.ext.commands import Cog, CommandInvokeError, UserInputError

from ..scenes import AspectIdError, NoCurrentSceneError

logger = logging.getLogger(__name__)

def setup(bot):
    bot.add_cog(ErrorHandlingCog())

_UNHANDLED_ERROR_EMOJI_NAMES = [
    'cold_face',
    'cold_sweat',
    'confounded',
    'grimacing',
    'head_bandage',
    'hot_face',
    'scream',
    'sob',
    'thermometer_face',
]

class ErrorHandlingCog(Cog):
    @Cog.listener()
    async def on_command_error(self, ctx, error):
        # If the command has its own error handling, just use that.
        if hasattr(ctx.command, 'on_error'):
            return

        if isinstance(error, UserInputError):
            message = f"{ctx.author.mention} Sorry, I didn't understand:\n\n"
            message += f"{quote(ctx.message)}\n\n"
            message += f"{punctuate(error)} Try **!help {ctx.invoked_with}** " \
                f"for more information. (Feel free to DM {ctx.me.mention}.)"

            await ctx.send(content=message)
            return

        if isinstance(error, CommandInvokeError):
            cause = error.__cause__

            if isinstance(cause, AspectIdError):
                message = f"{ctx.author.mention} Sorry, there's no aspect " \
                    f"in this scene with id {cause.aspect_id}."
                await ctx.send(content=message)
                return

            if isinstance(cause, NoCurrentSceneError):
                message = f"{ctx.author.mention} Sorry, there's no current " \
                    "scene in this channel. You can start a new scene using " \
                    "**!scene new**."
                await ctx.send(content=message)
                return

        emoji_name = random.choice(_UNHANDLED_ERROR_EMOJI_NAMES)
        message = f"{ctx.author.mention} Sorry, something unexpected went wrong.  :{emoji_name}:"
        await ctx.send(content=message)

        raise error

def quote(message):
    content = message.content
    return textwrap.indent(content, '> ', lambda line: True)

def punctuate(text):
    text = str(text)
    if text[-1] in '!?.':
        return text
    return f"{text}."

