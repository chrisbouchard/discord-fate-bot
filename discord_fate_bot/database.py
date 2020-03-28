from abc import ABC, abstractmethod
from bson.objectid import ObjectId
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin
from mashumaro.types import SerializationStrategy
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Dict

from .config import Config

async def get_database(config: Config) -> AsyncIOMotorDatabase:
    connection_url = config.mongo.url
    client = AsyncIOMotorClient(connection_url)
    database = client.discord_fate_bot

    # TODO: We should probably do this somewhere more convenient.
    await database.scenes.create_index(
        'channel_id',
        name='ix__scenes__channel_id',
        unique=True,
    )

    return database


class SerializableObjectId(SerializationStrategy):
    def _serialize(self, value: ObjectId) -> ObjectId:
        return value

    def _deserialize(self, value: ObjectId) -> ObjectId:
        return value

class SubDocument(ABC, DataClassDictMixin):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        annotations_dict = getattr(cls, '__annotations__', {})

        for attr in annotations_dict:
            if attr == ObjectId:
                annotations_dict[attr] = SerializableObjectId()

@dataclass
class Document(SubDocument):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        current_version = kwargs['version']

        orig_to_dict = getattr(cls, 'to_dict')
        orig_from_dict = getattr(cls, 'from_dict')

        def to_dict(self, *args, **kwargs):
            doc_dict = orig_to_dict(self, *args, **kwargs)
            if '_v' not in doc_dict:
                doc_dict['_v'] = current_version
            return doc_dict

        @classmethod
        def from_dict(cls, data, *args, **kwargs):
            version = data.get('_v', None)
            if version != current_version:
                return cls.from_old_dict(data, version)
            return orig_from_dict(data, *args, **kwargs)

        to_dict.__doc__ = orig_to_dict.__doc__
        from_dict.__doc__ = orig_from_dict.__doc__

        setattr(cls, 'to_dict', to_dict)
        setattr(cls, 'from_dict', from_dict)

    @classmethod
    def from_old_dict(cls, version):
        raise NotImplementedError

