from bson.objectid import ObjectId
from dataclasses import dataclass, field, replace
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from typing import Dict, Optional, Set

from .database import Document, SubDocument

@dataclass
class SceneAspect(SubDocument):
    name: str

@dataclass
class Scene(Document, version=1):
    channel_id: int
    message_ids: Set[int] = field(default_factory=set)
    description: Optional[str] = None
    aspects: Dict[str, SceneAspect] = field(default_factory=dict)
    next_aspect_id: int = 1

    def add_aspect(self, aspect: SceneAspect):
        self.aspects[str(self.next_aspect_id)] = aspect
        self.next_aspect_id += 1

    def get_aspect(self, aspect_id: int):
        return self.aspects[str(aspect_id)]

    def remove_aspect(self, aspect_id: int):
        del self.aspects[str(aspect_id)]

    def __str__(self):
        description = self.description or 'Current Scene'

        if self.aspects:
            aspects_str = '\n'.join(
                f'    •  {aspect.name} [{id}]'
                for id, aspect in self.aspects.items()
            )
        else:
            aspects_str = '    •  _No aspects. Add some with !aspect._'

        return f':clapper:  __**{description}**__\n{aspects_str}'

class SceneDao:
    database: AsyncIOMotorDatabase
    scenes: AsyncIOMotorCollection

    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.scenes = database.scenes

    async def find(self, channel_id: int) -> Optional[Scene]:
        scene_dict = await self.scenes.find_one({'channel_id': channel_id})

        if scene_dict is None:
            return None

        return Scene.from_dict(scene_dict)

    async def remove(self, channel_id: int):
        await self.scenes.delete_one({'channel_id': channel_id})

    async def save(self, scene: Scene):
        await self.scenes.replace_one(
            {'channel_id': scene.channel_id},
            scene.to_dict(),
            upsert=True
        )

