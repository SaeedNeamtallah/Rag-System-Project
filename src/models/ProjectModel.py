from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from pymongo.errors import DuplicateKeyError
from bson import ObjectId

from .db_schemas.project_shemas import ProjectSchema as Project





class ProjectModel:
    """
    Async MongoDB DAL for the "projects" collection.

    Design choices:
    - Strong typing for db & collection
    - Explicit indexes via Project.get_indexes()
    - Clear CRUD with safe returns
    - Pagination with metadata
    - Defensive error handling (DuplicateKeyError)
    - Timestamp management (created_at/updated_at)
    - Optional cascade delete to chunks collection
    """

    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str = "projects") -> None:
        self.db: AsyncIOMotorDatabase = db
        self.collection: AsyncIOMotorCollection = self.db[collection_name]
        self.chunks_collection: AsyncIOMotorCollection = self.db["chunks"]  # used for cascade delete

    @classmethod # why
    async def create_instance(cls, db: AsyncIOMotorDatabase, collection_name: str = "projects") -> "ProjectModel":
        instance = cls(db=db, collection_name=collection_name)  # __Init__ called
        await instance.init_collection()  # Collection initialized
        return instance

    async def init_collection(self) -> None:
        # Ensure collection exists and indexes are present
        _ = await self.db.list_collection_names()  # ensures connection works; not strictly needed to create collection
        for idx in Project.get_indexes():
            await self.collection.create_index(idx["key"], name=idx["name"], unique=idx.get("unique", False))

    # -------------------------
    # CRUD operations
    # -------------------------
    async def create_project(self, project: Project) -> Project:
        doc = project.model_dump(by_alias=True, exclude_unset=True)
        # keep timestamps consistent
        now = datetime.now(timezone.utc)
        doc.setdefault("created_at", now)
        doc["updated_at"] = now
        try:
            res = await self.collection.insert_one(doc)
        except DuplicateKeyError as e:
            raise ValueError(f"project_id '{project.project_id}' already exists") from e
        doc["_id"] = res.inserted_id
        return Project(**doc)

    async def get_by_project_id(self, project_id: str) -> Optional[Project]:
        rec = await self.collection.find_one({"project_id": project_id})
        return Project(**rec) if rec else None

    async def get_or_create(self, project_id: str) -> Project:
        existing = await self.get_by_project_id(project_id)
        if existing:
            return existing
        return await self.create_project(Project(project_id=project_id))

    async def update_by_project_id(self, project_id: str, data: Dict[str, Any]) -> Optional[Project]:
        # sanitize payload
        data = {k: v for k, v in (data or {}).items() if k not in {"_id", "id", "project_id", "created_at"}}
        if not data:
            return await self.get_by_project_id(project_id)
        data["updated_at"] = datetime.now(timezone.utc)
        rec = await self.collection.find_one_and_update(
            {"project_id": project_id},
            {"$set": data},
            return_document=True,
        )
        return Project(**rec) if rec else None

    async def delete_by_project_id(self, project_id: str, *, cascade_chunks: bool = True,
                                   chunk_fk_field: str = "chunk_project_id") -> bool:
        # Optionally delete related chunks first to avoid orphans
        if cascade_chunks:
            # First get the project to retrieve its ObjectId
            project = await self.get_by_project_id(project_id)
            if project and project.id:
                # Delete chunks using the project's ObjectId
                await self.chunks_collection.delete_many({chunk_fk_field: project.id})
        res = await self.collection.delete_one({"project_id": project_id})
        return res.deleted_count == 1

    # -------------------------
    # Listing & pagination
    # -------------------------
    async def list_projects(self, page: int = 1, page_size: int = 10,
                            *, sort: List[Tuple[str, int]] | None = None) -> Dict[str, Any]:
        page = max(page, 1)
        page_size = max(min(page_size, 100), 1)  # cap page_size to 100
        total = await self.collection.count_documents({})
        total_pages = (total + page_size - 1) // page_size
        sort = sort or [("created_at", -1), ("_id", -1)]
        cursor = (self.collection
                  .find({}, sort=sort)
                  .skip((page - 1) * page_size)
                  .limit(page_size))
        data: List[Project] = []
        async for doc in cursor:
            data.append(Project(**doc))
        return {
            "data": data,
            "meta": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1,
            },
        }


# -----------------------------
# Example usage (for reference)
# -----------------------------
# async def boot(db: AsyncIOMotorDatabase):
#     projects = await ProjectModel.create_instance(db)
#     await projects.create_project(Project(project_id="alpha", name="Alpha Project"))
#     item = await projects.get_or_create("beta", name="Beta")
#     item2 = await projects.update_by_project_id("beta", {"name": "Beta v2"})
#     listed = await projects.list_projects(page=1, page_size=5)
#     deleted = await projects.delete_by_project_id("alpha", cascade_chunks=True)
