"""
FastAPI application for RAG System.

This module initializes the FastAPI application with MongoDB, LLM providers,
and VectorDB providers for document processing and retrieval.
"""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from routes import base_router, datarouter ,nlp_router
from helper import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
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

    # Startup - PostgreSQL Connection
    logger.info("Connecting to PostgreSQL...")
    try:
        # Use asyncpg driver for async PostgreSQL connections
        postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"

        app.state.db_engine = create_async_engine(postgres_conn, echo=True)
        app.state.async_session = sessionmaker(
            bind=app.state.db_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        logger.info("✅ Connected to PostgreSQL")


    except Exception as e:
        logger.error(f"❌ Failed to connect to PostgreSQL: {e}")
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
        
        logger.info(f"✅ LLM providers initialized")
        logger.info(f"   Generation: {settings.GENERATION_BACKEND} / {settings.GENERATION_MODEL_ID}")
        logger.info(f"   Embedding: {settings.EMBEDDING_BACKEND} / {settings.EMBEDDING_MODEL_ID} / {settings.EMBEDDING_SIZE}D")
        logger.info(f"   Embedding client type: {type(app.state.embedding_client).__name__}")
        logger.info(f"   Embedding client size: {app.state.embedding_client.embedding_size}")
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

    # Startup - TemplateParser for RAG
    logger.info("Initializing TemplateParser...")
    try:
        from stores.llm.templete.templete_parser import TemplateParser
        app.state.template_parser = TemplateParser()
        logger.info("✅ TemplateParser initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize TemplateParser: {e}")
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