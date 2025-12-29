"""
Pydantic models for API Gateway requests and responses
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# Request Models
class QueryRequest(BaseModel):
    question: str = Field(..., description="The question to ask about the logs")
    limit: Optional[int] = Field(5, description="Maximum number of logs to retrieve", ge=1, le=50)
    time_filter: Optional[str] = Field(None, description="Time filter: 1h, 24h, 7d")
    service_filter: Optional[str] = Field(None, description="Filter by specific service")
    level_filter: Optional[str] = Field(None, description="Filter by log level: INFO, WARNING, ERROR, CRITICAL")

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query for semantic similarity")
    limit: Optional[int] = Field(5, description="Maximum number of results", ge=1, le=50)
    time_filter: Optional[str] = Field(None, description="Time filter: 1h, 24h, 7d")
    service_filter: Optional[str] = Field(None, description="Filter by specific service")
    level_filter: Optional[str] = Field(None, description="Filter by log level")

# Response Models
class LogEntry(BaseModel):
    service: str
    level: str
    message: str
    timestamp: str
    similarity: Optional[float] = None

class QueryResponse(BaseModel):
    answer: str
    query_type: str
    logs_found: int
    context_logs: List[LogEntry]
    filters_applied: Dict[str, Optional[str]]
    processing_time_ms: int

class SearchResponse(BaseModel):
    results: List[LogEntry]
    total_found: int
    query: str
    filters_applied: Dict[str, Optional[str]]
    processing_time_ms: int

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, str]
    version: str

class ErrorResponse(BaseModel):
    error: str
    message: str
    timestamp: datetime