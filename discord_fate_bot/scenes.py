from bson.objectid import ObjectId
from dataclasses import dataclass, field, replace
from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
from typing import Dict, List, Optional

from .database import Document

@dataclass
class SceneAspect
    id: int
    name: str

@dataclass
class Scene(Document, version=1):
    channel_id: int
    description: str = None
    aspects: List[SceneAspect] = field(default_factory=list)
    next_aspect_id: int = 1
    revision: int = 0

class SceneDao:
    database: AsyncIOMotorDatabase
    scenes: AsyncIOMotorCollection

    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.scenes = database.scenes

    async def find_by_channel_id(channel_id: int) -> Optional[Scene]:
        scene_dict = await self.scenes.find_one({'channel_id': channel_id})
        return Scene.from_dict(scene_dict)

    async def save_scene(scene: Scene):
        await self.scenes.replace_one(
            {'channel_id': channel_id},
            scene,
            upsert=True
        )

