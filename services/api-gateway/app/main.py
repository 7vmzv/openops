"""
OpenOps API Gateway - Main FastAPI Application
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime

from .config import settings
from .models import ErrorResponse
from .routers import health, query, search, metrics

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="""
    OpenOps API Gateway - AI-powered DevOps assistant
    
    This API provides endpoints to:
    - Query logs using natural language (LLM + RAG)
    - Search logs using semantic similarity
    - Check system health
    
    ## Usage Examples
    
    **Query logs with LLM:**
    ```
    POST /query/
    {
        "question": "What database errors happened in the last hour?",
        "time_filter": "1h",
        "limit": 5
    }
    ```
    
    **Search logs directly:**
    ```
    POST /search/
    {
        "query": "database timeout",
        "service_filter": "payment-service",
        "limit": 10
    }
    ```
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(query.router)
app.include_router(search.router)
app.include_router(metrics.router)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            message=str(exc),
            timestamp=datetime.utcnow()
        ).dict()
    )

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "OpenOps API Gateway",
        "version": settings.API_VERSION,
        "status": "running",
        "timestamp": datetime.utcnow(),
        "docs": "/docs",
        "health": "/health"
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info(f"Ollama host: {settings.OLLAMA_HOST}")
    logger.info(f"Qdrant host: {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True
    )