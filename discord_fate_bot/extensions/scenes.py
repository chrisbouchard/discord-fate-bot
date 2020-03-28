from discord import NotFound
from discord.ext.commands import Bot, Cog, Converter, Greedy, command, group
from discord.utils import escape_markdown, find
from typing import Dict, List, Optional, Union

from ..bot import DiscordFateBot
from ..scenes import Scene, SceneAspect, SceneDao

def setup(bot):
    if not isinstance(bot, DiscordFateBot):
        raise TypeError('Argument bot must be an instance of DiscordFateBot')
    bot.add_cog(ScenesCog(bot))


class AspectName(Converter):
    async def convert(self, ctx, name):
        if not name:
            raise BadArgument('An aspect must have a name')
        return str(name)


class ScenesCog(Cog, name='Scenes'):
    """Commands for managing scenes and scene aspects."""

    bot: DiscordFateBot
    scene_dao: SceneDao

    def __init__(self, bot: DiscordFateBot):
        self.bot = bot
        self.scene_dao = SceneDao(bot.database)


    @group(aliases=['s'], invoke_without_command=True)
    async def scene(self, ctx):
        pass

    @scene.command()
    async def new(self, ctx, *, description: str):
        """Create a new scene (replacing any existing scene)"""
        channel_id = ctx.channel.id
        existing_scene = await self.scene_dao.find(channel_id)

        if existing_scene is not None:
            await self._delete_scene_and_unpin_message(ctx, existing_scene)

        new_scene = Scene(
            channel_id=channel_id,
            description=description,
        )

        await self._save_scene_and_update_message(ctx, new_scene)

    @scene.command()
    async def end(self, ctx):
        """End the existing scene"""
        channel_id = ctx.channel.id
        scene = await self._find_scene_or_die(channel_id)
        await self._delete_scene_and_unpin_message(ctx, scene)


    @group(aliases=['a'], invoke_without_command=True)
    async def aspect(self, ctx):
        pass

    @aspect.command(aliases=['+'])
    async def add(self, ctx, *, name: AspectName):
        """Create a new aspect in the scene"""
        channel_id = ctx.channel.id
        scene = await self._find_scene_or_die(channel_id)

        scene.add_aspect(SceneAspect(name=name))
        await self._save_scene_and_update_message(ctx, scene)

        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

    @aspect.command(aliases=['-'])
    async def remove(self, ctx, aspect_ids: Greedy[int]):
        """Remove an aspect from the scene"""
        channel_id = ctx.channel.id
        scene = await self._find_scene_or_die(channel_id)

        for aspect_id in aspect_ids:
            scene.remove_aspect(aspect_id)
        await self._save_scene_and_update_message(ctx, scene)

        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')

    @aspect.command()
    async def modify(self, ctx, aspect_id: int, *, name: AspectName):
        """Modify an existing aspect"""
        channel_id = ctx.channel.id
        scene = await self._find_scene_or_die(channel_id)
        aspect = scene.get_aspect(aspect_id)

        if aspect is None:
            raise RuntimeError('No aspect in the current scene with that id')

        aspect.name = name
        await self._save_scene_and_update_message(ctx, scene)

        await ctx.message.add_reaction('\N{THUMBS UP SIGN}')


    async def _delete_scene_and_unpin_message(self, ctx, scene):
        self.scene_dao.remove(scene.channel_id)

        for message_id in scene.message_ids:
            try:
                message = await ctx.fetch_message(message_id)
                await message.unpin()
            except NotFound:
                # That's ok, if it doesn't exist we just won't unpin it.
                pass

    async def _find_scene_or_die(self, channel_id):
        scene = await self.scene_dao.find(channel_id)

        if scene is None:
            # TODO: Raise something better to send an error message
            raise RuntimeError('No current scene for this channel')

        return scene

    async def _save_scene_and_update_message(self, ctx, scene):
        await self.scene_dao.save(scene)

        # Make a copy because we many modify the set in the loop.
        copied_message_ids = scene.message_ids.copy()

        for message_id in copied_message_ids:
            try:
                existing_message = await ctx.fetch_message(
                    scene.message_id
                )
                await existing_message.edit(content=scene)

                edited_any = True
            except NotFound:
                # Ok, we couldn't find it so we couldn't edit it. But we'll
                # create a new message now. We'll remove the message id since
                # it's not valid anymore.
                self.message_ids.remove(message_id)

        if not scene.message_ids:
            new_message = await ctx.send(content=scene)
            scene.message_ids = { new_message.id }

            await new_message.pin()

            await self.scene_dao.save(scene)

