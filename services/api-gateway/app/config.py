"""
Configuration management for OpenOps API Gateway
"""

import os
from typing import Optional

class Settings:
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_TITLE: str = "OpenOps API Gateway"
    API_VERSION: str = "1.0.0"
    
    # Service URLs
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "localhost:11434")
    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))
    
    # LLM Service Configuration
    LLM_SERVICE_TIMEOUT: int = int(os.getenv("LLM_SERVICE_TIMEOUT", "30"))
    DEFAULT_SEARCH_LIMIT: int = int(os.getenv("DEFAULT_SEARCH_LIMIT", "5"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()