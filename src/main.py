from fastapi import FastAPI
from routes import base_router, datarouter

app = FastAPI(
    title="MiniRAG API",
    description="A lightweight Retrieval-Augmented Generation (RAG) application for document processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.include_router(base_router)
app.include_router(datarouter)

