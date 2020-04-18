import dataclasses
import logging

from asyncio import Lock
from collections import defaultdict
from discord import NotFound
from discord.ext.commands import BadArgument, Bot, Cog, Converter, Greedy, command, group, guild_only
from discord.utils import escape_markdown, find
from typing import Dict, List, Optional, Union

from ..bot import DiscordFateBot
from ..emojis import react_success
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

class AdjustInvokes(Converter):
    """An amount to adjust invokes."""

    async def convert(self, ctx, argument):
        if argument[:1] not in ('+', '-'):
            raise BadArgument('Expected: [+|-]VALUE')
        try:
            return int(argument)
        except ValueError:
            raise BadArgument('Expected a number')


class SceneManagementCog(Cog, name='Scene Management'):
    """Commands for managing scenes and scene aspects."""

    bot: DiscordFateBot
    scene_dao: SceneDao
    scene_locks: Dict[int, Lock]

    def __init__(self, bot: DiscordFateBot):
        self.bot = bot
        self.scene_dao = SceneDao(bot.database)
        self.scene_locks = defaultdict(Lock)


    async def cog_check(self, ctx):
        """Ensure that scene management is only implemented for guilds."""
        return await guild_only().predicate(ctx)

    async def cog_before_invoke(self, ctx):
        """Gate each command by a per-channel lock."""
        channel_id = ctx.channel.id
        await self.scene_locks[channel_id].acquire()

    async def cog_after_invoke(self, ctx):
        """Release the per-channel lock."""
        channel_id = ctx.channel.id
        self.scene_locks[channel_id].release()


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

    @scene.command(name='sync')
    async def scene_sync(self, ctx):
        """Sync the pinned scene message with the database"""
        channel_id = ctx.channel.id
        scene = await self.scene_dao.find(channel_id)
        await self._update_message(ctx, scene)
        await react_success(ctx.message)

    @scene.command(name='end')
    async def scene_end(self, ctx):
        """End the existing scene"""
        channel_id = ctx.channel.id
        scene = await self.scene_dao.find(channel_id)
        await self._delete_scene_and_unpin_message(ctx, scene)
        await react_success(ctx.message)


    @group(invoke_without_command=True)
    async def aspect(self, ctx, *, name: AspectName):
        """Create a new aspect in the scene"""
        channel_id = ctx.channel.id
        scene = await self.scene_dao.find(channel_id)

        new_aspect = SceneAspect(name=name)

        scene.add_aspect(new_aspect)
        await self._save_scene_and_update_message(ctx, scene)
        await react_success(ctx.message)

    @group(invoke_without_command=True)
    async def boost(self, ctx, *, name: AspectName):
        """Create a new boost in the scene"""
        channel_id = ctx.channel.id
        scene = await self.scene_dao.find(channel_id)

        new_aspect = SceneAspect(name=name, boost=True, invokes=1)

        scene.add_aspect(new_aspect)
        await self._save_scene_and_update_message(ctx, scene)
        await react_success(ctx.message)

    @aspect.command(name='remove', aliases=['rem'])
    async def aspect_remove(self, ctx, aspect_ids: Greedy[int]):
        """Remove an aspect from the scene"""
        channel_id = ctx.channel.id
        scene = await self.scene_dao.find(channel_id)

        for aspect_id in aspect_ids:
            scene.remove_aspect(aspect_id)

        await self._save_scene_and_update_message(ctx, scene)
        await react_success(ctx.message)

    @aspect.command(name='rename')
    async def aspect_rename(self, ctx, aspect_id: int, *, name: AspectName):
        """Rename an existing aspect"""
        channel_id = ctx.channel.id
        scene = await self.scene_dao.find(channel_id)

        aspect = scene.get_aspect(aspect_id)
        aspect.name = name

        scene.replace_aspect(aspect_id, aspect)
        await self._save_scene_and_update_message(ctx, scene)
        await react_success(ctx.message)

    @boost.command(name='upgrade')
    async def boost_upgrade(self, ctx, aspect_id: int, *, name: AspectName = None):
        """Upgrade an existing boost to a full aspect, optionally reaming it."""
        channel_id = ctx.channel.id
        scene = await self.scene_dao.find(channel_id)

        aspect = scene.get_aspect(aspect_id)

        if not aspect.boost:
            raise BadArgument(f'Aspect with id {aspect_id} is not a boost.')

        aspect.boost = False

        if name:
            aspect.name = name

        scene.replace_aspect(aspect_id, aspect)
        await self._save_scene_and_update_message(ctx, scene)
        await react_success(ctx.message)

    @boost.command(name='downgrade')
    async def boost_downgrade(self, ctx, aspect_id: int, *, name: AspectName = None):
        """Downgrade an existing aspect to a boost, optionally reaming it."""
        channel_id = ctx.channel.id
        scene = await self.scene_dao.find(channel_id)

        aspect = scene.get_aspect(aspect_id)

        if aspect.boost:
            raise BadArgument(f'Aspect with id {aspect_id} is already a boost.')

        aspect.boost = True

        if name:
            aspect.name = name

        scene.replace_aspect(aspect_id, aspect)
        await self._save_scene_and_update_message(ctx, scene)
        await react_success(ctx.message)

    @group(invoke_without_command=True)
    async def invoke(self, ctx, aspect_id: int):
        """Invoke an aspect. This will remove an invoke if available."""
        channel_id = ctx.channel.id
        scene = await self.scene_dao.find(channel_id)

        aspect = scene.get_aspect(aspect_id)

        if aspect.invokes > 0:
            aspect.invokes -= 1

        scene.replace_aspect(aspect_id, aspect)
        await self._save_scene_and_update_message(ctx, scene)
        await react_success(ctx.message)

    @invoke.command(name='add')
    async def invoke_add(self, ctx, amount: Optional[AdjustInvokes], aspect_id: int):
        """Add invokes (by default one) to an aspect.

        AMOUNT

          The optional amount argument should start with "+" or "-" to indicate
          adding or removing invokes. An aspect cannot wind up with fewer than
          zero invokes.
        """
        channel_id = ctx.channel.id
        scene = await self.scene_dao.find(channel_id)

        aspect = scene.get_aspect(aspect_id)
        aspect.invokes += (amount if amount is not None else 1)
        aspect.validate(f'The result for aspect {aspect_id} is not valid.')

        scene.replace_aspect(aspect_id, aspect)
        await self._save_scene_and_update_message(ctx, scene)
        await react_success(ctx.message)


    async def _delete_scene_and_unpin_message(self, ctx, scene):
        await self.scene_dao.remove(scene.channel_id)

        for message_id in scene.message_ids:
            try:
                message = await ctx.fetch_message(message_id)
                await message.unpin()
            except NotFound:
                # That's ok, if it doesn't exist we just won't unpin it.
                pass

        # Clear out the list of messages to be safe. There are none now.
        scene.message_ids.clear()

    async def _save_scene_and_update_message(self, ctx, scene):
        await self.scene_dao.save(scene)
        await self._update_message(ctx, scene)

    async def _update_message(self, ctx, scene):
        # Make a copy because we many modify the set in the loop.
        copied_message_ids = scene.message_ids.copy()

        for message_id in copied_message_ids:
            try:
                existing_message = await ctx.fetch_message(message_id)
                await existing_message.edit(content=scene)

                edited_any = True
            except NotFound:
                # Ok, we couldn't find it so we couldn't edit it. We'll remove
                # the message id since it's not valid anymore. If there are no
                # valid message ids, we'll create a new message below.
                self.message_ids.remove(message_id)

        if not scene.message_ids:
            new_message = await ctx.send(content=scene)
            scene.message_ids = { new_message.id }

            await new_message.pin()

            await self.scene_dao.save(scene)

