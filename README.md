# MiniRAG Application

A lightweight Retrieval-Augmented Generation (RAG) application built with FastAPI that allows you to upload documents, process them into searchable chunks, and query them using AI language models. This application provides a foundation for building document-based AI applications with proper text processing and retrieval capabilities.

## 🏗️ Architecture Overview


### Core Components

```
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

- **Backend Framework**: FastAPI (async Python web framework)
- **Database**: MongoDB with Motor (async driver)  
- **Document Processing**: LangChain (text splitting and document loading)
- **PDF Processing**: PyMuPDF (efficient PDF text extraction)
- **Data Validation**: Pydantic (request/response schemas)
- **File Handling**: aiofiles (async file operations)
- **Containerization**: Docker + Docker Compose

## 📁 Project Structure

```
src/
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Python dependencies
├── helpers/
│   └── config.py              # Application configuration management
├── routes/
│   ├── base.py                # Basic API endpoints (health, version)
│   ├── data.py                # File upload and processing endpoints
│   └── schemas/
│       └── data.py            # Request/response data schemas
├── controllers/
│   ├── BaseController.py      # Common controller functionality
│   ├── DataController.py      # File validation and storage
│   ├── ProjectController.py   # Project directory management
│   └── ProcessController.py   # Document processing and chunking
├── models/
│   ├── db_schemas/
│   │   ├── project.py         # Project database model
│   │   └── datachunk.py       # Text chunk database model
│   └── enums/
│       ├── ResponseEnum.py    # Standardized response messages
│       └── ProcessingEnums.py # Document type definitions
└── assets/
    └── files/                 # File storage (organized by project)
        └── {project_id}/      # Project-specific file directories

docker/
├── docker-compose.yml         # MongoDB service definition
└── mongodb_data/              # Persistent MongoDB storage
```

## 🚀 API Endpoints

### Base Endpoints
- `GET /api/v1/` - Application information and health check

### Data Management  
- `POST /api/v1/data/upload/{project_id}` - Upload files to a project
- `POST /api/v1/data/process/{project_id}` - Process files into text chunks

### Request/Response Examples

**Upload File:**
```bash
curl -X POST "http://localhost:8000/api/v1/data/upload/my_project" \
     -F "file=@document.pdf"
```

**Process File:**
```bash
curl -X POST "http://localhost:8000/api/v1/data/process/my_project" \
     -H "Content-Type: application/json" \
     -d '{
         "file_id": "abc123_document.pdf",
         "chunk_size": 500,
         "over_lap": 50
     }'
```

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Application Configuration
APP_NAME=MiniRAG
APP_VERSION=1.0.0

# OpenAI Configuration (for future embedding/LLM integration)
OPENAI_API_KEY=your_openai_api_key_here

# File Upload Configuration
FILE_ALLOWED_TYPES=["application/pdf", "text/plain"]
FILE_MAX_SIZE=10                    # Maximum file size in MB
FILE_DEFAULT_CHUNK_SIZE=1000        # Default chunk size for text splitting

# Database Configuration
MONGODB_URI=mongodb://localhost:27007
MONGODB_DB_NAME=minirag_db
```

## Prerequisites & Installation

### Prerequisites
- Python 3.8+
- Docker & Docker Compose
- Git
### Installation Steps
uvicorn main:app --reload --host 0.0.0.0 --port 8080
uvicorn main:app --reload


sudo apt install python3-venv -y
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
