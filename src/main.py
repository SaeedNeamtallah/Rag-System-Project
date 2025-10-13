from contextlib import asynccontextmanager
from fastapi import FastAPI
from routes import base_router, datarouter
from motor import motor_asyncio
from helper import get_settings, Settings
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = get_settings()
    logger.info("Connecting to MongoDB...")
    
    client = motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
    db = client[settings.MONGO_DB_NAME]
    
    # Verify connection
    await client.admin.command('ping')
    logger.info(f"✅ Connected to MongoDB: {settings.MONGO_DB_NAME}")
    
    # Store in app state
    app.state.db = db
    app.state.client = client
    
    yield
    
    # Shutdown
    logger.info("Closing MongoDB connection...")
    client.close()
    logger.info("✅ MongoDB connection closed")


app = FastAPI(
    title="MiniRAG API",
    description="A lightweight Retrieval-Augmented Generation (RAG) application for document processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan #used above in the asynccontextmanager function
)

app.include_router(base_router)
app.include_router(datarouter)

