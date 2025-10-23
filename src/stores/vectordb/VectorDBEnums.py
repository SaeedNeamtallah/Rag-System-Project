"""VectorDB enumerations for providers and distance methods."""

from enum import Enum


class VectorDBEnums(Enum):
    """Supported VectorDB providers."""
    QDRANT = "QDRANT"


class DistanceMethodEnums(Enum):
    """Distance calculation methods for vector similarity."""
    COSINE = "cosine"
    DOT = "dot"