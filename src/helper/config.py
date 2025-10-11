from pydantic_settings import BaseSettings 
from typing import Optional
from pathlib import Path

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    FILE_MAX_SIZE: Optional[int]  # 10 MB
    FILE_ALLOWED_TYPES: str
    CHUNK_SIZE: Optional[int]  # characters
    CHUNK_OVERLAP: Optional[int]  # characters



    class Config:
        # Get the path to the .env file in the src directory
        env_file = str(Path(__file__).resolve().parent.parent / ".env")
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    return Settings()

