# RAG System Project

A robust Retrieval-Augmented Generation (RAG) system built with FastAPI that enables document upload, intelligent processing, and AI-powered retrieval. Upload files, automatically process them into searchable chunks stored in MongoDB, and retrieve contextual information for your AI applications.

## 🏗️ Architecture Overview

### Core Components

```text
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Client App    │────▶│   FastAPI API   │────▶│   Controllers   │
│  (Upload/Query) │     │   Routes        │     │  (Business      │
└─────────────────┘     └─────────────────┘     │   Logic)        │
                                                └─────────┬───────┘
                                                          │
                                                          ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   MongoDB       │◀────│   Data Models   │◀────│   File Storage  │
│  (Chunks &      │     │  (Pydantic)     │     │  (Project-based │
│   Projects)     │     └─────────────────┘     │   Organization) │
└─────────────────┘                             └─────────────────┘
                                                          ▲
                                                          │
                                                          ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │   LangChain     │────▶│   Document      │
                        │  Text Splitter  │     │   Loaders       │
                        │  (Chunking)     │     │  (PDF, TXT)     │
                        └─────────────────┘     └─────────────────┘
```

### Data Flow

1. **Document Upload** → File validation → Unique naming → Project storage
2. **Document Processing** → Content extraction → Text chunking → Metadata preservation  
3. **Data Storage** → MongoDB chunks → Project organization → Retrieval indexing

## 🛠️ Technical Stack

- **Backend Framework**: FastAPI with async/await patterns
- **Database**: MongoDB with Motor (async Python driver)
- **Document Processing**: LangChain (text splitting, document loading)
- **PDF Processing**: PyMuPDF (FitzPDF) for efficient PDF extraction
- **Data Validation**: Pydantic v2 with custom validators
- **File Handling**: aiofiles for async I/O operations
- **Containerization**: Docker & Docker Compose
- **Python Version**: 3.12+
- **Additional Libraries**: pymongo, aiofiles, python-dotenv, python-multipart

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
│   └── schemas/
│       ├── __init__.py
│       └── dataproces_schemas.py    # Request/response schemas
├── controllers/
│   ├── __init__.py
│   ├── BaseContoller.py             # Base controller functionality
│   ├── DataController.py            # File validation & storage
│   ├── ProcessController.py         # Document processing & chunking
│   └── __pycache__/
├── models/
│   ├── __init__.py
│   ├── BaseDataModel.py             # Base async MongoDB model
│   ├── ChunkModel.py                # Chunks collection DAL (async)
│   ├── ProjectModel.py              # Projects collection DAL (async)
│   ├── AssetModel.py                # Assets collection DAL (async)
│   ├── db_schemas/
│   │   ├── __init__.py
│   │   ├── chunks_schemas.py        # ChunkSchema with indexes
│   │   ├── project_shemas.py        # ProjectSchema with indexes
│   │   ├── asset.py                 # AssetSchema with indexes
│   │   └── __pycache__/
│   ├── enums/
│   │   ├── __init__.py
│   │   ├── ProcesseEnums.py         # Document type enums
│   │   ├── ResponseEnums.py         # API response enums
│   │   └── __pycache__/
│   └── __pycache__/
└── assets/
    └── files/                       # File storage (organized by project)
        └── {project_id}/            # Project-specific directories

docker/
├── docker-compose.yml               # MongoDB service definition
├── .env.example                     # Environment template
├── .gitignore                       # Docker-specific gitignore
└── mongo-data/                      # MongoDB persistent storage

.gitignore                          # Root gitignore
README.md                           # This file
LICENSE                            # Project license
```

## 🚀 API Endpoints

### Base Endpoints

- `GET /api/v1/` - Application information and health check

### Data Management Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/data/upload/{project_id}` | Upload files to a project (returns asset_id) |
| `POST` | `/api/v1/data/processall/{project_id}` | Process all files in project, save chunks to MongoDB |
| `POST` | `/api/v1/data/processone/{project_id}` | Process single file, save chunks with optional reset |

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

## 🔧 Configuration

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

# Database Configuration
MONGO_URI=mongodb://root:example@localhost:27017
MONGO_DB_NAME=rag_system_db
```

### Docker Environment (.env in docker/)

```bash
# MongoDB Credentials
MONGO_INITDB_ROOT_USERNAME=root
MONGO_INITDB_ROOT_PASSWORD=example
```

⚠️ **Security Note**: Change default MongoDB credentials in production!

## 📋 Prerequisites & Installation

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Git

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

4. **Start MongoDB with Docker Compose:**
   ```bash
   cd ../docker
   docker-compose up -d
   ```

5. **Create `.env` file in src/:**
   ```bash
   cd ../src
   # Edit the environment variables as shown in Configuration section
   ```

6. **Run the application:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

7. **Access the API:**
   - API Documentation: `http://localhost:8000/docs`
   - ReDoc Documentation: `http://localhost:8000/redoc`
   - API Base URL: `http://localhost:8000/api/v1`

## 📊 Database Schema

### Collections

#### `projects` Collection
```json
{
  "_id": ObjectId,
  "project_id": "string (unique)",
  "created_at": "ISO datetime",
  "updated_at": "ISO datetime"
}
```

#### `chunks` Collection
```json
{
  "_id": ObjectId,
  "chunk_text": "string",
  "chunk_metadata": "object",
  "chunk_order": "integer (≥ 1)",
  "chunk_project_id": "ObjectId (ref: projects._id)",
  "created_at": "ISO datetime",
  "updated_at": "ISO datetime"
}
```

#### `assets` Collection
```json
{
  "_id": ObjectId,
  "asset_project_id": "ObjectId (ref: projects._id)",
  "asset_type": "string (e.g., 'file')",
  "asset_name": "string (filename)",
  "asset_size": "integer (bytes)",
  "asset_config": "object (optional)",
  "asset_pushed_at": "ISO datetime"
}
```

### Indexes

- `projects`: Unique index on `project_id`
- `chunks`: Index on `chunk_project_id`
- `assets`: Composite unique index on (`asset_project_id`, `asset_name`)

## 🐛 Recent Fixes & Improvements

### v1.0.0 Updates
- ✅ Fixed data persistence: chunks and projects now properly saved to MongoDB
- ✅ Implemented async factory pattern for all models (ChunkModel, ProjectModel, AssetModel)
- ✅ Added comprehensive error handling in all endpoints
- ✅ Implemented proper MongoDB schema validation with Pydantic
- ✅ Added automatic index creation for all collections
- ✅ Fixed asset tracking with dedicated AssetModel
- ✅ Improved file upload with validation and error responses
- ✅ Added project lookup before processing with 404 handling
- ✅ Implemented batch chunk insertion for performance

## 🧪 Testing

### Manual Testing

```bash
# 1. Upload a PDF file
curl -X POST "http://localhost:8000/api/v1/data/upload/test_project" \
     -F "file=@sample.pdf"

# 2. Process the uploaded file
curl -X POST "http://localhost:8000/api/v1/data/processone/test_project" \
     -H "Content-Type: application/json" \
     -d '{
       "file_id": "abc123_sample.pdf",
       "chunk_size": 1000,
       "overlap_size": 100,
       "do_reset": false
     }'

# 3. Verify chunks in MongoDB
# Connect to MongoDB and check: db.chunks.find({"chunk_project_id": ObjectId("...")})
```

## 🚀 Deployment

### Production Considerations

1. **Environment Variables**: Update all `.env` files with production values
2. **MongoDB**: Use MongoDB Atlas or managed service with authentication
3. **Security**: Enable HTTPS, add CORS policies, implement rate limiting
4. **Logging**: Configure centralized logging for production monitoring
5. **Docker**: Build optimized production images with multi-stage builds

## 📝 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) file for details.

## 👥 Contributors

- Saeed Neamtallah (@SaeedNeamtallah)
