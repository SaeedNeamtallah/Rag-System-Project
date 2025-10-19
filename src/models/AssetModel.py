from typing import List
from .BaseDataModel import BaseDataModel
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from .db_schemas.asset import Asset as AssetSchema
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError


class AssetModel(BaseDataModel):
    """
    Async MongoDB DAL for the "assets" collection.

    Design choices:
    - Inherits from BaseDataModel for common functionality
    - Strong typing for db & collection
    - Explicit indexes via Asset.get_indexes()
    - Clear CRUD with safe returns
    - Pagination with metadata
    - Defensive error handling (DuplicateKeyError)
    - Timestamp management (created_at/updated_at)
    """

    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str = "assets") -> None:
        super().__init__(db, collection_name)

    @classmethod
    async def create_instance(cls, db: AsyncIOMotorDatabase, collection_name: str = "assets") -> "AssetModel":
        instance = cls(db=db, collection_name=collection_name)
        await instance.init_collection()
        return instance
    
    async def init_collection(self) -> None:
        # Ensure collection exists and indexes are present
        _ = await self.db.list_collection_names()  # ensures connection works; not strictly needed to create collection
        for idx in AssetSchema.get_indexes():
            await self.collection.create_index(idx["key"], name=idx["name"], unique=idx.get("unique", False))

    # -------------------------
    # CRUD operations
    # -------------------------
    async def create_asset(self, asset: AssetSchema) -> AssetSchema:
        doc = asset.model_dump(by_alias=True, exclude_unset=True)
        # keep timestamps consistent
        now = datetime.now(timezone.utc)
        doc.setdefault("created_at", now)
        doc["updated_at"] = now
        try:
            res = await self.collection.insert_one(doc)
        except DuplicateKeyError as e:
            raise ValueError(f"asset with given unique fields already exists") from e
        doc["_id"] = res.inserted_id
        return AssetSchema(**doc)
    

    async def get_all_project_assets(self, project_id: str) -> List[AssetSchema]:
            cursor = self.collection.find({"asset_project_id": project_id})
            assets = []
            try:
                async for doc in cursor:
                    assets.append(AssetSchema(**doc))
                return assets
            except Exception as e:
                raise RuntimeError(f"Error retrieving assets for project_id '{project_id}': {e}") from e
            
    
        
    async def get_asset(self, asset_id: str) -> AssetSchema:
        
        doc = await self.collection.find_one({"_id": asset_id})
        if doc:
            return AssetSchema(**doc)
        return None
    
    async def delete_asset(self, asset_id: str) -> int:
        try:
            res = await self.collection.delete_one({"_id": asset_id})
            return res.deleted_count
        except Exception as e:
            print(f"Error deleting asset with id '{asset_id}': {e}")
            return 0
        
    async def delete_assets_by_project_id(self, project_id: str) -> int:
        """Delete all assets associated with a project_id"""
        try:
            res = await self.collection.delete_many({"asset_project_id": project_id})
            return res.deleted_count
        except Exception as e:
            print(f"Error deleting assets for project_id '{project_id}': {e}")
            return 0
    