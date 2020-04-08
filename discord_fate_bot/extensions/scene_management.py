import dataclasses
import logging
import random

from discord import NotFound
from discord.ext.commands import Bot, Cog, Converter, Greedy, command, group
from discord.utils import escape_markdown, find
from typing import Dict, List, Optional, Union

from ..bot import DiscordFateBot
from ..emojis import SUCCESS_EMOJIS
from ..scenes import NoCurrentSceneError, Scene, SceneAspect, SceneDao

logger = logging.getLogger(__name__)

def setup(bot):
    if not isinstance(bot, DiscordFateBot):
        raise TypeError('Argument bot must be an instance of DiscordFateBot')
    bot.add_cog(SceneManagementCog(bot))


class AspectName(Converter):
    async def convert(self, ctx, name):
        if not name:
            raise BadArgument('An aspect must have a name')
        if '\n' in name:
            raise BadArgument('An aspect name must be one line')
        return str(name)


class BoostTag(Converter):
    async def convert(self, ctx, tag):
        if tag in ('boost', '-boost'):
            raise BadArgument('Expected: boost')
        return ('boost', tag[0] == '-')

class InvokesTag(Converter):
    async def convert(self, ctx, tag):
        key, _, value = tag.partition('=')

        if key != 'invokes' or value is None:
            raise BadArgument('Expected: invokes=COUNT')
        return ('invokes', int(value))

AspectTag = Union[BoostTag, InvokesTag]


class SceneManagementCog(Cog, name='Scene Management'):
    """Commands for managing scenes and scene aspects."""

    bot: DiscordFateBot
    scene_dao: SceneDao

    def __init__(self, bot: DiscordFateBot):
        self.bot = bot
        self.scene_dao = SceneDao(bot.database)


    @group(invoke_without_command=True)
    async def scene(self, ctx, *, description: str = None):
        """Create a new scene (replacing any existing scene)"""
        channel_id = ctx.channel.id

        try:
            existing_scene = await self.scene_dao.find(channel_id)
            await self._delete_scene_and_unpin_message(ctx, existing_scene)
        except NoCurrentSceneError:
            pass

        new_scene = Scene(
            channel_id=channel_id,
            description=description,
        )

        await self._save_scene_and_update_message(ctx, new_scene)

    @scene.command(name='end')
    async def scene_end(self, ctx):
        """End the existing scene"""
        channel_id = ctx.channel.id
        scene = await self.scene_dao.find(channel_id)
        await self._delete_scene_and_unpin_message(ctx, scene)
        await self._react_ok(ctx)


    @group(invoke_without_command=True)
    async def aspect(self, ctx, tags: Greedy[AspectTag], *, name: AspectName):
        """Create a new aspect in the scene"""
        channel_id = ctx.channel.id
        scene = await self.scene_dao.find(channel_id)

        # TODO: Do some error checking (negative invokes, boost without
        # invokes, etc.)
        tags_dict = dict(tags)

        new_aspect = SceneAspect(name=name, **tags_dict)

        scene.add_aspect(new_aspect)
        await self._save_scene_and_update_message(ctx, scene)
        await self._react_ok(ctx)

    @aspect.command(name='remove', aliases=['rem'])
    async def aspect_remove(self, ctx, aspect_ids: Greedy[int]):
        """Remove an aspect from the scene"""
        channel_id = ctx.channel.id
        scene = await self.scene_dao.find(channel_id)

        for aspect_id in aspect_ids:
            scene.remove_aspect(aspect_id)

        await self._save_scene_and_update_message(ctx, scene)
        await self._react_ok(ctx)

    @aspect.command(name='modify', aliases=['mod'])
    async def aspect_modify(self, ctx, aspect_id: int, tags: Greedy[AspectTag], *, name: AspectName = None):
        """Modify an existing aspect"""
        channel_id = ctx.channel.id
        scene = await self.scene_dao.find(channel_id)
        aspect = scene.get_aspect(aspect_id)

        if aspect is None:
            raise RuntimeError('No aspect in the current scene with that id')

        # TODO: Do some error checking (negative invokes, boost without
        # invokes, etc.)
        if tags:
            tags_dict = dict(tags)
            aspect = dataclasses.replace(aspect, **tags_dict)

        if name:
            aspect = dataclasses.replace(aspect, name=name)

        scene.replace_aspect(aspect_id, aspect)
        await self._save_scene_and_update_message(ctx, scene)
        await self._react_ok(ctx)


    async def _delete_scene_and_unpin_message(self, ctx, scene):
        await self.scene_dao.remove(scene.channel_id)

        for message_id in scene.message_ids:
            try:
                message = await ctx.fetch_message(message_id)
                await message.unpin()
            except NotFound:
                # That's ok, if it doesn't exist we just won't unpin it.
                pass

    async def _react_ok(self, ctx):
        await ctx.message.add_reaction(random.choice(SUCCESS_EMOJIS))

    async def _save_scene_and_update_message(self, ctx, scene):
        await self.scene_dao.save(scene)

        # Make a copy because we many modify the set in the loop.
        copied_message_ids = scene.message_ids.copy()

        for message_id in copied_message_ids:
            try:
                existing_message = await ctx.fetch_message(message_id)
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

