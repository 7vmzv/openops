"""
Dependency injection for API Gateway services
"""

import sys
import os
from functools import lru_cache

# Add the LLM service to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'llm-service'))

from llm_service import LLMService
from qdrant_client import QdrantClient
from .config import settings

@lru_cache()
def get_llm_service() -> LLMService:
    """Get LLM service instance (cached)"""
    return LLMService(
        ollama_host=settings.OLLAMA_HOST,
        qdrant_host=settings.QDRANT_HOST,
        qdrant_port=settings.QDRANT_PORT
    )

@lru_cache()
def get_qdrant_client() -> QdrantClient:
    """Get Qdrant client instance (cached)"""
    return QdrantClient(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT
    )