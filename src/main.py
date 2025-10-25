"""
FastAPI application for RAG System.

This module initializes the FastAPI application with MongoDB, LLM providers,
and VectorDB providers for document processing and retrieval.
"""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from motor import motor_asyncio

from routes import base_router, datarouter ,nlp_router
from helper import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan (startup and shutdown).

    Handles:
    - MongoDB connection
    - LLM provider initialization
    - VectorDB provider initialization
    - Graceful shutdown of all connections
    """
    settings = get_settings()

    # Startup - MongoDB Connection
    logger.info("Connecting to MongoDB...")
    try:
        client = motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
        db = client[settings.MONGO_DB_NAME]

        # Verify connection
        await client.admin.command("ping")
        logger.info(f"✅ Connected to MongoDB: {settings.MONGO_DB_NAME}")

        # Store in app state
        app.state.db = db
        app.state.client = client
    except Exception as e:
        logger.error(f"❌ Failed to connect to MongoDB: {e}")
        raise

    # Startup - LLM Provider Factory
    logger.info("Initializing LLM providers...")
    try:
        llm_factory = LLMProviderFactory(settings)

        # Initialize generation provider
        app.state.generation_client = llm_factory.get_provider(settings.GENERATION_BACKEND)
        app.state.generation_client.set_generation_model(settings.GENERATION_MODEL_ID)

        # Initialize embedding provider
        app.state.embedding_client = llm_factory.get_provider(settings.EMBEDDING_BACKEND)
        app.state.embedding_client.set_embedding_model(
            settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_SIZE
        )

        logger.info("✅ LLM providers initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize LLM providers: {e}")
        raise

    # Startup - VectorDB Provider Factory
    logger.info("Initializing VectorDB provider...")
    try:
        vectordb_factory = VectorDBProviderFactory(settings)
        app.state.vector_db_client = vectordb_factory.get_provider(settings.VECTOR_DB_BACKEND)
        app.state.vector_db_client.connect()
        logger.info("✅ VectorDB provider initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize VectorDB provider: {e}")
        raise

    yield

    # Shutdown - Close all connections
    logger.info("Shutting down application...")

    # Close VectorDB connection
    try:
        if hasattr(app, "vector_db_client") and app.state.vector_db_client:
            app.state.vector_db_client.disconnect()
            logger.info("✅ VectorDB connection closed")
    except Exception as e:
        logger.error(f"❌ Error closing VectorDB connection: {e}")

    # Close MongoDB connection
    try:
        if hasattr(app.state, "client") and app.state.client:
            app.state.client.close()
            logger.info("✅ MongoDB connection closed")
    except Exception as e:
        logger.error(f"❌ Error closing MongoDB connection: {e}")


# Initialize FastAPI application
app = FastAPI(
    title="MiniRAG API",
    description="A lightweight Retrieval-Augmented Generation (RAG) application for document processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Include routers
app.include_router(base_router)
app.include_router(datarouter)
app.include_router(nlp_router)