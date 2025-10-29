# RAG System Project

A robust Retrieval-Augmented Generation (RAG) system built with FastAPI that enables document upload, intelligent processing, vector-based similarity search, and AI-powered answer generation. Upload files, automatically process them into searchable chunks with embeddings, store in PostgreSQL with pgvector and Qdrant vector database, and retrieve contextual answers powered by LLMs for your AI applications.

## 🏗️ Architecture Overview

### Core Components

```text
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Client App    │────▶│   FastAPI API   │────▶│   Controllers   │
│  (Upload/Query) │     │   Routes        │     │  (Business      │
└─────────────────┘     └─────────────────┘     │   Logic)        │
                                                └─────────┬───────┘
                                                          │
                        ┌─────────────────────────────────┼───────────────┐
                        ▼                                 ▼               ▼
                ┌───────────────┐              ┌──────────────┐  ┌──────────────┐
                │  PostgreSQL   │              │ LLM Providers│  │ VectorDB     │
                │  + pgvector   │              │ (OpenAI,     │  │ (Qdrant)     │
                │  (Chunks,     │              │  Cohere)     │  │              │
                │   Projects,   │              │              │  │              │
                │   Assets)     │              │              │  │              │
                └───────────────┘              └──────────────┘  └──────────────┘
                        ▲                              ▲                  ▲
                        │                              │                  │
                        └──────────┬───────────────────┴──────────────────┘
                                   ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   LangChain     │────▶│   Document      │
                        │  Text Splitter  │     │   Loaders       │
                        │  (Chunking)     │     │  (PDF, TXT)     │
                        └─────────────────┘     └─────────────────┘
                                   ▲
                                   │
                        ┌─────────────────┐
                        │   File Storage  │
                        │  (Project-based │
                        │   Organization) │
                        └─────────────────┘
```

### Data Flow 


1. **Document Upload** → File validation → Unique naming → Project storage
2. **Document Processing** → Content extraction → Text chunking → Metadata preservation
3. **Data Storage** → PostgreSQL (via SQLAlchemy async) → Project organization → Asset tracking
4. **Vector Embeddings** → LLM Provider (Cohere/OpenAI) → Generate embeddings → Store in Qdrant VectorDB
5. **Similarity Search** → Query vectors → VectorDB search → Retrieve top-k relevant chunks
6. **Answer Generation** → Prompt construction with context → LLM generation → AI-powered answers

### Provider Architecture

The system uses a **Factory Pattern** for extensible provider management:

**LLM Providers:**

- Abstract `LLMInterface` defines the contract
- `LLMProviderFactory` creates provider instances
- Support for OpenAI and Cohere (easily extensible)
- Unified API for text generation and embeddings
- Multi-language prompt templates with dynamic imports

**VectorDB Providers:**

- Abstract `VectorDBInterface` defines the contract
- `VectorDBProviderFactory` creates provider instances
- Qdrant implementation for vector storage
- Support for collection management and similarity search
- Configurable distance metrics (cosine, dot product)

## 🛠️ Technical Stack

- **Backend Framework**: FastAPI with async/await patterns and lifespan context management
- **Database**: PostgreSQL 18.0 with pgvector extension (v0.8.1) for vector similarity
- **ORM**: SQLAlchemy 2.0 with async support (asyncpg driver)
- **Database Migrations**: Alembic for schema version control
- **Vector Database**: Qdrant for vector storage and similarity search
- **LLM Providers**: OpenAI and Cohere with factory pattern (supports custom OpenAI-compatible APIs)
- **Template Engine**: Multi-language prompt template system with Python string.Template
- **Document Processing**: LangChain (text splitting, document loading)
- **PDF Processing**: PyMuPDF (FitzPDF) for efficient PDF extraction
- **Data Validation**: Pydantic v2 with custom validators
- **File Handling**: aiofiles for async I/O operations
- **Containerization**: Docker & Docker Compose
- **Python Version**: 3.12+
- **Additional Libraries**: asyncpg, sqlalchemy, alembic, aiofiles, python-dotenv, python-multipart, qdrant-client, openai, cohere, langchain

## 📁 Project Structure 

```text
src/
├── main.py                          # FastAPI application & lifespan context
├── requirements.txt                 # Python dependencies
├── helper/
│   ├── __init__.py
│   └── config.py                    # Application settings management
├── routes/
│   ├── __init__.py
│   ├── base.py                      # Health/version endpoints
│   ├── data_route.py                # File upload & processing endpoints
│   ├── nlp.py                       # RAG endpoints (push, search, generate)
│   └── schemas/
│       ├── __init__.py
│       ├── dataproces_schemas.py    # Request/response schemas
│       └── nlp.py                   # NLP/RAG schemas
├── controllers/
│   ├── __init__.py
│   ├── BaseContoller.py             # Base controller functionality
│   ├── DataController.py            # File validation & storage
│   ├── ProcessController.py         # Document processing & chunking
│   └── NLPController.py             # RAG logic (search, answer generation)
├── models/
│   ├── __init__.py
│   ├── BaseDataModel.py             # Base async SQLAlchemy model
│   ├── ChunkModel.py                # DataChunk DAL (async)
│   ├── ProjectModel.py              # Project DAL (async)
│   ├── AssetModel.py                # Asset DAL (async)
│   ├── db_schemas/
│   │   ├── __init__.py              # Public schema exports
│   │   ├── rag/                     # RAG database schemas
│   │   │   ├── alembic.ini          # Alembic configuration
│   │   │   ├── alembic/             # Migration scripts
│   │   │   │   ├── env.py           # Migration environment
│   │   │   │   └── versions/        # Migration versions
│   │   │   └── schemas/
│   │   │       ├── __init__.py
│   │   │       ├── rag_base.py      # SQLAlchemy Base
│   │   │       ├── chunks_schemas.py # DataChunk model
│   │   │       ├── project_shemas.py # Project model
│   │   │       └── asset.py         # Asset model
│   ├── enums/
│   │   ├── __init__.py
│   │   ├── ProcesseEnums.py         # Document type enums
│   │   ├── ResponseEnums.py         # API response enums
│   │   └── __pycache__/
│   └── __pycache__/
├── stores/                          # External service providers
│   ├── llm/                         # LLM providers (OpenAI, Cohere)
│   │   ├── __init__.py
│   │   ├── LLMInterface.py          # Abstract LLM interface
│   │   ├── LLMEnums.py              # LLM provider enums
│   │   ├── LLMProviderFactory.py    # Factory for LLM providers
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   ├── OpenAIProvider.py    # OpenAI implementation
│   │   │   └── CoHereProvider.py    # Cohere implementation
│   │   └── templete/
│   │       ├── __init__.py
│   │       ├── templete_parser.py   # Template parser for prompts
│   │       └── locales/
│   │           ├── ar/              # Arabic templates
│   │           │   ├── __init__.py
│   │           │   └── rag.py
│   │           └── en/              # English templates
│   │               ├── __init__.py
│   │               └── rag.py
│   └── vectordb/                    # Vector database providers
│       ├── __init__.py
│       ├── VectorDBInterface.py     # Abstract VectorDB interface
│       ├── VectorDBEnums.py         # VectorDB provider enums
│       ├── VectorDBProviderFactory.py # Factory for VectorDB providers
│       └── providers/
│           ├── __init__.py
│           └── QdrantDBProvider.py  # Qdrant implementation
└── assets/
    └── files/                       # File storage (organized by project)
        └── {project_id}/            # Project-specific directories

docker/
├── docker-compose.yml               # PostgreSQL + MongoDB services
├── .env                             # Database credentials
├── DATABASE_CONNECTIONS.md          # Connection guide for DBeaver/pgAdmin
├── QUICK_REFERENCE.txt              # Quick reference card
└── postgres-data/                   # PostgreSQL persistent storage

.gitignore                          # Root gitignore
README.md                           # This file
LICENSE                            # Project license
```

## 🚀 API Endpoints

### Base Endpoints

- `GET /api/v1/` - Application information and health check health

### Data Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/data/upload/{project_id}` | Upload files to a project (returns asset_id) |
| `POST` | `/api/v1/data/processall/{project_id}` | Process all files in project, save chunks to MongoDB |
| `POST` | `/api/v1/data/processone/{project_id}` | Process single file, save chunks with optional reset |

### NLP/RAG Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/nlp/push` | Push documents to vector database with embeddings |
| `POST` | `/api/v1/nlp/search` | Search for similar documents using vector similarity |
| `POST` | `/api/v1/nlp/generate` | Generate AI-powered answers based on query and context |

### Response Structure

All endpoints return JSON responses with status indicators:

```json
{
  "status": "success_code",
  "message": "Descriptive message",
  "data": {}
}
```

### Request/Response Examples

**Upload File:**

```bash
curl -X POST "http://localhost:8000/api/v1/data/upload/my_project" \
     -F "file=@document.pdf"

# Response:
{
  "status": "file_upload_success",
  "file_path": "/path/to/file",
  "file_id": "unique_filename",
  "asset_id": "507f1f77bcf86cd799439011"
}
```

**Process Single File:**

```bash
curl -X POST "http://localhost:8000/api/v1/data/processone/my_project" \
     -H "Content-Type: application/json" \
     -d '{
       "file_id": "abc123_document.pdf",
       "chunk_size": 1000,
       "overlap_size": 100,
       "do_reset": false
     }'

# Response:
{
  "status": "processing_success",
  "total_chunks": 42,
  "inserted_chunks": 42,
  "chunks": [...]
}
```

**Process All Files:**

```bash
curl -X POST "http://localhost:8000/api/v1/data/processall/my_project"

# Response:
{
  "status": "processing_success",
  "total_files": 5,
  "processed_files": 5,
  "failed_files": 0,
  "total_chunks": 150,
  "inserted_chunks": 150
}
```

**Push Documents to Vector Database:**

```bash
curl -X POST "http://localhost:8000/api/v1/nlp/push" \
     -H "Content-Type: application/json" \
     -d '{
       "project_id": "my_project",
       "do_reset": false
     }'

# Response:
{
  "status": "success",
  "message": "Successfully pushed 150 chunks to vector database",
  "total_chunks": 150,
  "embedding_model": "embed-v4.0",
  "vector_dimension": 256
}
```

**Search Similar Documents:**

```bash
curl -X POST "http://localhost:8000/api/v1/nlp/search" \
     -H "Content-Type: application/json" \
     -d '{
       "project_id": "my_project",
       "query": "What is the main topic?",
       "top_k": 5
     }'

# Response:
{
  "status": "success",
  "results": [
    {
      "chunk_text": "The main topic discusses...",
      "score": 0.89,
      "chunk_id": "507f1f77bcf86cd799439011"
    },
    ...
  ],
  "total_results": 5
}
```

**Generate AI-Powered Answer:**

```bash
curl -X POST "http://localhost:8000/api/v1/nlp/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "project_id": "my_project",
       "query": "What is the main topic?",
       "language": "en",
       "top_k": 5
     }'

# Response:
{
  "status": "success",
  "answer": "Based on the documents, the main topic discusses...",
  "context_documents_count": 5
}
```

## 🔧 Configuration

### RAG Workflow

The RAG system follows a complete pipeline from document upload to AI-powered answer generation:

1. **Upload Documents**: Upload PDF or text files to project-specific directories
2. **Process & Chunk**: Extract text and split into semantic chunks with overlap
3. **Generate Embeddings**: Create vector embeddings using Cohere or OpenAI
4. **Store Vectors**: Index embeddings in Qdrant vector database for similarity search
5. **Query Processing**: Convert user queries into embeddings
6. **Retrieve Context**: Find top-k most relevant document chunks via vector similarity
7. **Prompt Construction**: Build context-aware prompts with multi-language templates
8. **Generate Answers**: Use LLM to generate answers based on retrieved context

### Key Features

- **Multi-Provider Support**: Switch between OpenAI and Cohere for embeddings and generation
- **Custom LLM Endpoints**: Use OpenAI-compatible APIs (e.g., local Ollama models via ngrok)
- **Vector Search**: Similarity search with configurable distance metrics (cosine, dot product)
- **Template System**: Multi-language prompt templates with dynamic variable substitution
- **Async Processing**: Non-blocking I/O for efficient file processing and database operations
- **Lazy Loading**: Optimized startup with on-demand provider initialization
- **Flexible Chunking**: Configurable chunk sizes and overlap for optimal retrieval
- **Project Isolation**: Separate vector collections per project for organization

### Environment Variables

Create a `.env` file in the `src/` directory with the following variables:

```bash
# Application Configuration
APP_NAME=RAG-System
APP_VERSION=1.0.0

# File Upload Configuration
FILE_ALLOWED_TYPES=["application/pdf", "text/plain"]
FILE_MAX_SIZE=50                    # Maximum file size in MB
CHUNK_SIZE=1000                     # Default chunk size in characters
CHUNK_OVERLAP=100                   # Default overlap between chunks

# Database configuration
POSTGRES_USERNAME=postgres
POSTGRES_PASSWORD=minirag
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_MAIN_DATABASE=ai_vectors
DATABASE_URL=postgresql+asyncpg://postgres:minirag@localhost:5433/ai_vectors

# Vector Database Configuration
VECTOR_DB_PROVIDER=QDRANT           # Vector database provider
VECTOR_DB_PATH=./assets/files/qdrant_db  # Path for Qdrant storage
VECTOR_DB_DISTANCE_METHOD=cosine    # Distance method: cosine or dot

# Embedding Configuration
EMBEDDING_BACKEND=COHERE            # Embedding provider: OPENAI or COHERE
EMBEDDING_MODEL=embed-v4.0          # Cohere embedding model
EMBEDDING_MODEL_SIZE=256            # Embedding dimension size (256 for Cohere, 1536 for OpenAI)

# Generation/LLM Configuration
GENERATION_BACKEND=OPENAI           # Generation provider: OPENAI or COHERE
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_URL=https://api.openai.com/v1  # Optional custom endpoint (supports local Ollama)
COHERE_API_KEY=your_cohere_api_key

# LLM Default Parameters
INPUT_DEFAULT_MAX_CHARACTERS=16000  # Maximum input characters for prompts
GENERATION_DEFAULT_MAX_TOKENS=1000  # Maximum tokens for generated responses
GENERATION_DEFAULT_TEMPERATURE=0.1  # Temperature for text generation
```

### Docker Environment (.env in docker/)

```bash
# PostgreSQL Configuration
VECTOR_PGUSER=postgres
VECTOR_PGPASSWORD=minirag
VECTOR_PGDB=ai_vectors
VECTOR_PGPORT=5433

# MongoDB Configuration (if needed)
MONGO_INITDB_ROOT_USERNAME=root
MONGO_INITDB_ROOT_PASSWORD=example
```

⚠️ **Security Note**: Change default database credentials in production!

## 📋 Prerequisites & Installation

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Git
- PostgreSQL client (optional, for direct database access)

### Quick Start

1. **Clone the repository:**

   ```bash
   git clone https://github.com/SaeedNeamtallah/Rag-System-Project.git
   cd Rag-System-Project
   ```

2. **Create and activate virtual environment:**

   ```bash
   # On Linux/Mac
   python3 -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   cd src
   pip install -r requirements.txt
   ```

4. **Start PostgreSQL with Docker Compose:**

   ```bash
   cd ../docker
   docker-compose up -d
   ```

5. **Run database migrations:**

   ```bash
   cd ../src/models/db_schemas/rag
   alembic upgrade head
   ```

6. **Create `.env` file in src/:**

   ```bash
   cd ../../../
   # Edit the environment variables as shown in Configuration section
   ```

7. **Run the application:**

   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

8. **Access the API:**
   - API Documentation: `http://localhost:8000/docs`
   - ReDoc Documentation: `http://localhost:8000/redoc`
   - API Base URL: `http://localhost:8000/api/v1`

## 📊 Database Schema

### PostgreSQL Tables (with pgvector extension)

#### `projects` Table

```sql
CREATE TABLE projects (
    project_id SERIAL PRIMARY KEY,
    project_uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);
```

#### `assets` Table

```sql
CREATE TABLE assets (
    asset_id SERIAL PRIMARY KEY,
    asset_uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    asset_project_id INTEGER NOT NULL REFERENCES projects(project_id),
    asset_type VARCHAR(50) NOT NULL,
    asset_name VARCHAR(255) NOT NULL,
    asset_size INTEGER,
    asset_config JSONB,
    asset_pushed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE,
    UNIQUE (asset_project_id, asset_name)
);
```

#### `chunks` Table

```sql
CREATE TABLE chunks (
    chunk_id SERIAL PRIMARY KEY,
    chunk_uuid UUID UNIQUE NOT NULL DEFAULT gen_random_uuid(),
    chunk_text TEXT NOT NULL,
    chunk_metadata JSONB,
    chunk_order INTEGER NOT NULL,
    chunk_project_id INTEGER NOT NULL REFERENCES projects(project_id),
    chunk_asset_id INTEGER NOT NULL REFERENCES assets(asset_id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX ix_chunk_project_id ON chunks(chunk_project_id);
CREATE INDEX ix_chunk_asset_id ON chunks(chunk_asset_id);
```

### Schema Features

- **UUID Support**: All tables have UUID fields for external references
- **JSONB**: Flexible metadata storage for chunks and asset configurations
- **Foreign Keys**: Proper relationships between projects, assets, and chunks
- **Timestamps**: Automatic tracking of creation and update times
- **Indexes**: Optimized for common query patterns

## 🐛 Recent Fixes & Improvements

### v2.0.0 Updates - PostgreSQL Migration

- ✅ **Database Migration**: Migrated from MongoDB to PostgreSQL 18.0 with pgvector extension
- ✅ **SQLAlchemy Integration**: Implemented async SQLAlchemy 2.0 with asyncpg driver
- ✅ **Alembic Migrations**: Added database versioning and schema migration support
- ✅ **pgvector Extension**: Enabled vector similarity search capabilities in PostgreSQL
- ✅ **Schema Refactoring**: Proper foreign key relationships between projects, assets, and chunks
- ✅ **Async Models**: Updated all models to use async sessionmaker patterns
- ✅ **Database Sessions**: Fixed session management - using `self.db_client()` correctly
- ✅ **Asset Tracking**: Implemented proper asset creation before chunk insertion
- ✅ **Import Structure**: Unified imports through `models.db_schemas` package
- ✅ **Type Conversion**: Fixed project_id type handling (int vs str in path operations)
- ✅ **Connection Documentation**: Created comprehensive guides for DBeaver/pgAdmin connections
- ✅ **Vector Dimension Validation**: Added embedding dimension mismatch detection
- ✅ **Error Handling**: Improved NOT NULL constraint handling and clearer error messages

### v1.1.0 Updates - RAG Implementation

- ✅ Implemented complete RAG pipeline (Retrieval-Augmented Generation)
- ✅ Added vector database integration with Qdrant
- ✅ Implemented embedding generation with Cohere and OpenAI support
- ✅ Added similarity search functionality for document retrieval
- ✅ Implemented AI-powered answer generation with context
- ✅ Added multi-language prompt template system
- ✅ Support for custom OpenAI-compatible APIs (e.g., local Ollama)
- ✅ Optimized startup performance with lazy loading
- ✅ Added singleton TemplateParser in lifespan context
- ✅ Fixed dimension mismatch issues between embedding providers
- ✅ Improved error handling and logging throughout RAG pipeline
- ✅ Added comprehensive NLP endpoints (/push, /search, /generate)

### v1.0.0 Updates - Data Processing

- ✅ Fixed data persistence: chunks and projects now properly saved to database
- ✅ Implemented async factory pattern for all models
- ✅ Added comprehensive error handling in all endpoints
- ✅ Implemented proper schema validation with Pydantic
- ✅ Added automatic index creation for all tables
- ✅ Fixed asset tracking with dedicated AssetModel
- ✅ Improved file upload with validation and error responses
- ✅ Added project lookup before processing with 404 handling
- ✅ Implemented batch chunk insertion for performance
- ✅ Added LLM provider abstraction with OpenAI and Cohere support
- ✅ Added VectorDB provider abstraction with Qdrant support
- ✅ Implemented factory pattern for extensible provider management
- ✅ Added comprehensive documentation and type hints across all modules

## 🧪 Testing

### Manual Testing - Complete RAG Workflow

```bash
# 1. Upload a PDF file
curl -X POST "http://localhost:8000/api/v1/data/upload/test_project" \
     -F "file=@sample.pdf"

# 2. Process the uploaded file into chunks
curl -X POST "http://localhost:8000/api/v1/data/processone/test_project" \
     -H "Content-Type: application/json" \
     -d '{
       "file_id": "abc123_sample.pdf",
       "chunk_size": 1000,
       "overlap_size": 100,
       "do_reset": false
     }'

# 3. Push chunks to vector database with embeddings
curl -X POST "http://localhost:8000/api/v1/nlp/push" \
     -H "Content-Type: application/json" \
     -d '{
       "project_id": "test_project",
       "do_reset": false
     }'

# 4. Search for similar documents
curl -X POST "http://localhost:8000/api/v1/nlp/search" \
     -H "Content-Type: application/json" \
     -d '{
       "project_id": "test_project",
       "query": "What is the main topic?",
       "top_k": 5
     }'

# 5. Generate AI-powered answer
curl -X POST "http://localhost:8000/api/v1/nlp/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "project_id": "test_project",
       "query": "What is the main topic?",
       "language": "en",
       "top_k": 5
     }'

# 6. Verify data in PostgreSQL
# Option 1: Using psql
docker exec -it vector-postgres psql -U postgres -d ai_vectors
# SELECT * FROM projects WHERE project_id = 3;
# SELECT COUNT(*) FROM chunks WHERE chunk_project_id = 3;

# Option 2: Using DBeaver (see docker/DATABASE_CONNECTIONS.md)
```

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Update all `.env` files with production values
   - Use strong MongoDB credentials (not default root/example)
   - Add valid API keys for OpenAI/Cohere
   - Configure appropriate token limits and chunk sizes
   - Set VECTOR_DB_PATH to persistent storage location

2. **MongoDB**: Use MongoDB Atlas or managed service with authentication
   - Enable authentication and encryption
   - Configure backup and recovery procedures
   - Set up replica sets for high availability

3. **Vector Database**: Configure Qdrant for production
   - Use persistent storage with regular backups
   - Monitor memory usage for large collections
   - Configure distance metrics based on embedding provider

4. **Security**: 
   - Enable HTTPS with valid SSL certificates
   - Add CORS policies for allowed origins
   - Implement rate limiting and request throttling
   - Secure API keys with environment variables or secret management
   - Add authentication/authorization for endpoints

5. **Logging**: 
   - Configure centralized logging for production monitoring
   - Set up log rotation to manage disk space
   - Monitor error rates and performance metrics
   - Track embedding and generation costs

6. **Docker**: 
   - Build optimized production images with multi-stage builds
   - Use Docker secrets for sensitive data
   - Configure health checks and restart policies
   - Set resource limits for containers

7. **Performance**:
   - Use connection pooling for MongoDB
   - Cache embeddings to reduce API calls
   - Implement async processing for large file uploads
   - Monitor and optimize prompt sizes for LLM calls

## 📝 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## 👥 Contributors

- Saeed Neamtallah (@SaeedNeamtallah)
