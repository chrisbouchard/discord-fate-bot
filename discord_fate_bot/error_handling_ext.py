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
            await ctx.send(f"{player.mention} Sorry, I didn't understand: `{original_command}`")


def setup(bot):
    bot.add_cog(ErrorHandlingCog())

