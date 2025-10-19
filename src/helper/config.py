from pydantic_settings import BaseSettings 
from typing import Optional, List
from pathlib import Path
import json

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    FILE_MAX_SIZE: Optional[int]  # 10 MB
    FILE_ALLOWED_TYPES: str
    CHUNK_SIZE: Optional[int]  # characters
    CHUNK_OVERLAP: Optional[int]  # characters'
    MONGO_URI: str
    MONGO_DB_NAME: str

    @property
    def file_allowed_types_list(self) -> List[str]:
        """Parse FILE_ALLOWED_TYPES from string to list"""
        if isinstance(self.FILE_ALLOWED_TYPES, str):
            try:
                return json.loads(self.FILE_ALLOWED_TYPES)
            except json.JSONDecodeError:
                # Fallback: split by comma
                return [ext.strip() for ext in self.FILE_ALLOWED_TYPES.split(',')]
        return self.FILE_ALLOWED_TYPES

    class Config:
        # Get the path to the .env file in the src directory
        env_file = str(Path(__file__).resolve().parent.parent / ".env")
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    return Settings()

