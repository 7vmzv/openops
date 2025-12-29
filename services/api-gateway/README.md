# OpenOps API Gateway

FastAPI-based API Gateway for the OpenOps DevOps assistant.

## Features

- **LLM Queries** (`/query/`) - Natural language queries with RAG
- **Vector Search** (`/search/`) - Direct semantic search in logs
- **Health Checks** (`/health/`) - Service health monitoring
- **Auto Documentation** (`/docs`) - Interactive API documentation

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
# Development mode (with auto-reload)
python -m app.main

# Or using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Test the API

```bash
# Run test suite
python test_api.py

# Or test manually
curl http://localhost:8000/health/
```

## API Endpoints

### Health Check
```bash
GET /health/
```

### Query Logs (LLM + RAG)
```bash
POST /query/
{
    "question": "What database errors happened?",
    "limit": 5,
    "time_filter": "1h",
    "service_filter": "payment-service",
    "level_filter": "ERROR"
}
```

### Search Logs (Vector Search)
```bash
POST /search/
{
    "query": "database timeout",
    "limit": 10,
    "service_filter": "api-gateway"
}
```

### Get Available Services
```bash
GET /search/services
```

## Configuration

Environment variables:

- `API_HOST` - Server host (default: 0.0.0.0)
- `API_PORT` - Server port (default: 8000)
- `OLLAMA_HOST` - Ollama service host (default: localhost:11434)
- `QDRANT_HOST` - Qdrant host (default: localhost)
- `QDRANT_PORT` - Qdrant port (default: 6333)
- `LOG_LEVEL` - Logging level (default: INFO)

## Documentation

- **Interactive docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Architecture

```
FastAPI App
├── /health/     → Health checks
├── /query/      → LLM Service (RAG)
├── /search/     → Direct Qdrant search
└── /docs        → Auto-generated docs
```

The API Gateway acts as a unified interface to the OpenOps system, providing clean REST endpoints for all functionality.