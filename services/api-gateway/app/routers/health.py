"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from datetime import datetime
import requests

from ..models import HealthResponse
from ..config import settings
from ..dependencies import get_qdrant_client

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/", response_model=HealthResponse)
async def health_check(qdrant_client=Depends(get_qdrant_client)):
    """Check the health of all services"""
    
    services = {}
    
    # Check Qdrant
    try:
        collections = qdrant_client.get_collections()
        services["qdrant"] = "healthy"
    except Exception as e:
        services["qdrant"] = f"unhealthy: {str(e)}"
    
    # Check Ollama
    try:
        response = requests.get(f"http://{settings.OLLAMA_HOST}/api/tags", timeout=5)
        services["ollama"] = "healthy" if response.status_code == 200 else "unhealthy"
    except Exception as e:
        services["ollama"] = f"unhealthy: {str(e)}"
    
    # Overall status
    overall_status = "healthy" if all("healthy" in status for status in services.values()) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        services=services,
        version=settings.API_VERSION
    )