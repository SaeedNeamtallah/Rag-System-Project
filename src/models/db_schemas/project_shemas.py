from pydantic import BaseModel, Field
from typing import  Optional
from bson import ObjectId

class ProjectSchema(BaseModel):
    """
    MongoDB document schema for Project collection.
    
    The _id field is MongoDB's default primary key:
    - default_factory=ObjectId: Automatically generates a new ObjectId when creating a document
    - alias="id": Allows using 'id' in JSON instead of '_id' for better API compatibility
    
    Example:
        When you create: {"id": "...", "name": "Project 1"}
        MongoDB stores:  {"_id": ObjectId("..."), "name": "Project 1"}
    """

    id: Optional[ObjectId] = Field(default=None, alias="_id")
    project_id: str = Field(..., min_length=1)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        # Allow arbitrary types like ObjectId
        arbitrary_types_allowed = True
        # Enable population by field name (allows using 'id' or '_id')
        populate_by_name = True
        # JSON schema customization for ObjectId
        json_encoders = {
            ObjectId: str  # Convert ObjectId to string in JSON responses
        }


