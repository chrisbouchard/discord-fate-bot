import textwrap

from discord.ext.commands import Cog, UserInputError

class ErrorHandlingCog(Cog):
    @Cog.listener()
    async def on_command_error(self, ctx, error):
        # If the command has its own error handling, just use that.
        if hasattr(ctx.command, 'on_error'):
            return

        if isinstance(error, UserInputError):
            message = f"{ctx.author.mention} Sorry, I didn't understand:\n\n"
            message += f"{quote(ctx.message)}\n\n"
            message += f'{punctuate(error)} Try **!help {ctx.invoked_with}** for more information. (Feel free to DM {ctx.me.mention}.)'

            await ctx.send(message)
            return

        raise error


def setup(bot):
    bot.add_cog(ErrorHandlingCog())


def quote(message):
    content = message.content
    return textwrap.indent(content, '> ', lambda line: True)

def punctuate(text):
    text = str(text)
    if text[-1] in '!?.':
        return text
    return f"{text}."

