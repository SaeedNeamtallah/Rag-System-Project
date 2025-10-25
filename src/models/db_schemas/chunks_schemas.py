from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId

class ChunkSchema(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., ge=1)  # Greater than or equal to 1
    chunk_project_id: ObjectId

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        json_encoders = {
            ObjectId: str
        }
    
    @classmethod
    def get_chunk_indexes(cls):
        return [
            {
                "key": [("chunk_project_id", 1)],
                "name": "project_id_chunk_index_1",
                "unique": False
            }
        ]
    
class RetrievedDocument(BaseModel):
    text: str
    score: float
    
