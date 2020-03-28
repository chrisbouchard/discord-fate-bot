from abc import ABC, abstractmethod
from bson.objectid import ObjectId
from dataclasses import dataclass, field
from mashumaro import DataClassDictMixin
from mashumaro.types import SerializationStrategy
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Dict

from .config import Config

def get_database(config: Config) -> AsyncIOMotorDatabase:
    connection_url = config.mongo.url
    client = AsyncIOMotorClient(connection_url)
    return client.discord_fate_bot


class SerializableObjectId(SerializationStrategy):
    def _serialize(self, value: ObjectId) -> ObjectId:
        return value

    def _deserialize(self, value: ObjectId) -> ObjectId:
        return value

@dataclass
class Document(ABC, DataClassDictMixin):
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
            return orig_from_dict(cls, data, *args, **kwargs)

        setattr(cls, 'to_dict', to_dict)
        setattr(cls, 'from_dict', from_dict)

        for attr in cls.__annotations__:
            if attr == ObjectId:
                cls.__annotations__[attr] = SerializableObjectId()

    @classmethod
    def from_old_dict(cls, version):
        raise NotImplementedError

