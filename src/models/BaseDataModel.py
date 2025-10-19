# file: models/BaseDataModel.py
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from helper.config import get_settings, Settings

class BaseDataModel:
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str) -> None:
        self.settings: Settings = get_settings()
        self.db: AsyncIOMotorDatabase = db
        self.collection: AsyncIOMotorCollection = db[collection_name]
