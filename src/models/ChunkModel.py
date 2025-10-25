from __future__ import annotations

from typing import List, Optional
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

from .db_schemas.chunks_schemas import ChunkSchema as Chunk

class ChunkModel:
    """
    Async MongoDB DAL for the "chunks" collection.

    Design choices:
    - Strong typing for db & collection
    - Explicit indexes via Chunk.get_chunk_indexes()
    - Clear CRUD with safe returns
    - Pagination with metadata
    - Defensive error handling (DuplicateKeyError)
    - Timestamp management (created_at/updated_at)
    """

    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str = "chunks") -> None:
        self.db: AsyncIOMotorDatabase = db
        self.collection: AsyncIOMotorCollection = self.db[collection_name]

    @classmethod #Initialization with async operations: Python classes can't use async in __init__, so this method works around that limitation by providing an async factory method.
    async def create_instance(cls, db: AsyncIOMotorDatabase, collection_name: str = "chunks") -> "ChunkModel":
        instance = cls(db=db, collection_name=collection_name)
        await instance.init_collection()
        return instance

    async def init_collection(self) -> None:
        # Ensure collection exists and indexes are present
        _ = await self.db.list_collection_names()  # ensures connection works; not strictly needed to create collection
        for idx in Chunk.get_chunk_indexes():
            await self.collection.create_index(idx["key"], name=idx["name"], unique=idx.get("unique", False))

    # -------------------------
    # CRUD operations
    # -------------------------
    async def create_chunk(self, chunk: Chunk) -> Chunk:
        doc = chunk.model_dump(by_alias=True, exclude_unset=True)
        # keep timestamps consistent
        now = datetime.now(timezone.utc)
        doc.setdefault("created_at", now)
        doc["updated_at"] = now
        try:
            res = await self.collection.insert_one(doc)
        except DuplicateKeyError as e:
            raise ValueError("chunk with given unique fields already exists") from e
        doc["_id"] = res.inserted_id
        return Chunk(**doc)
    
    async def get_chunk(self, chunk_id: str) -> Optional[Chunk]:
        doc = await self.collection.find_one({"_id": ObjectId(chunk_id)})
        if doc:
            return Chunk(**doc)
        return None

    async def insert_many_chunks(self, chunks: List[Chunk], batch_size: int = 100) -> List[Chunk]:
        chunk_docs = [chunk.model_dump(by_alias=True, exclude_unset=True) for chunk in chunks]
        now = datetime.now(timezone.utc)
        for doc in chunk_docs:
            doc.setdefault("created_at", now)
            doc["updated_at"] = now
        result = []
        for i in range(0, len(chunk_docs), batch_size):
            batch = chunk_docs[i:i + batch_size]
            res = await self.collection.insert_many(batch)
            for j, inserted_id in enumerate(res.inserted_ids):
                doc = batch[j]
                doc["_id"] = inserted_id
                result.append(Chunk(**doc))
        return result

    async def del_chunks_by_project_id(self, project_object_id: ObjectId) -> int:
        """Delete all chunks associated with a project's ObjectId"""
        result = await self.collection.delete_many({"chunk_project_id": project_object_id})
        return result.deleted_count
    
    async def get_project_chunks_paginated(
        self,
        project_object_id: ObjectId,
        page: int = 1,
        page_size: int = 50
    ) -> List[Chunk]:
        """Retrieve chunks for a project with pagination"""
        skip = (page - 1) * page_size
        cursor = self.collection.find({"chunk_project_id": project_object_id}).skip(skip).limit(page_size)
        chunks = [Chunk(**doc) async for doc in cursor]

        return chunks
    
