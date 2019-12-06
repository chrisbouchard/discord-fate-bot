from discord.ext.commands import Cog, UserInputError

class ErrorHandlingCog(Cog):
    @Cog.listener()
    async def on_command_error(self, ctx, error):
        # If the command has its own error handling, just use that.
        if hasattr(ctx.command, 'on_error'):
            return

        player = ctx.author
        original_command = ctx.message.content

        if isinstance(error, UserInputError):
            message = f"{player.mention} Sorry, I didn't understand: `{original_command}`"

            if hasattr(error, 'message'):
                message += f'\n{error.message}'

            message += f'\nTry `!help {ctx.invoked_with}` for more information.'

            await ctx.send(message)
            return

        raise error


def setup(bot):
    bot.add_cog(ErrorHandlingCog())

