"""VectorDB Provider Factory for creating vector database instances."""

from .providers.QdrantDBProvider import QdrantDBProvider
from .VectorDBEnums import VectorDBEnums
from ...controllers import BaseContoller
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorDBProviderFactory:
    """Factory for creating VectorDB provider instances."""

    def __init__(self, config: dict):
        """Initialize factory with configuration."""
        self.config = config
        self.base_controller = BaseContoller()
        self.db_path = self.base_controller.get_database_path(
            self.config.VECTOR_DB_PATH
        )

    def get_provider(self, provider_name: str):
        """Get a VectorDB provider instance by name."""
        if provider_name == VectorDBEnums.QDRANT.value:
            db_path = self.db_path
            distance_method = self.config.VECTOR_DB_DISTANCE_METHOD

            return QdrantDBProvider(db_path, distance_method)

        else:
            raise ValueError(f"Unsupported VectorDB provider: {provider_name}")
