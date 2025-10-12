# MiniRAG Application

A lightweight Retrieval-Augmented Generation (RAG) application built with FastAPI that allows you to upload documents, process them into searchable chunks, and query them using AI language models. This application provides a foundation for building document-based AI applications with proper text processing and retrieval capabilities.

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

- **Backend Framework**: FastAPI (async Python web framework)
- **Database**: MongoDB with Motor (async driver)  
- **Document Processing**: LangChain (text splitting and document loading)
- **PDF Processing**: PyMuPDF (efficient PDF text extraction)
- **Data Validation**: Pydantic (request/response schemas)
- **File Handling**: aiofiles (async file operations)
- **Containerization**: Docker + Docker Compose

## 📁 Project Structure

```text
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
- `POST /api/v1/data/processall/{project_id}` - Process all files in a project
- `POST /api/v1/data/processone/{project_id}` - Process a single file

### Request/Response Examples

**Upload File:**

```bash
curl -X POST "http://localhost:8000/api/v1/data/upload/my_project" \
     -F "file=@document.pdf"
```

**Process Single File:**

```bash
curl -X POST "http://localhost:8000/api/v1/data/processone/my_project" \
     -H "Content-Type: application/json" \
     -d '{
         "file_id": "abc123_document.pdf",
         "chunk_size": 1000,
         "overlap_size": 100
     }'
```

**Process All Files:**

```bash
curl -X POST "http://localhost:8000/api/v1/data/processall/my_project"
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

4. **Create `.env` file:**

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run the application:**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access the API:**

- API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
