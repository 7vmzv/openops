"""
Search endpoints for direct vector search
"""

import time
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from typing import List

from ..models import SearchRequest, SearchResponse, LogEntry
from ..dependencies import get_llm_service

router = APIRouter(prefix="/search", tags=["search"])

@router.post("/", response_model=SearchResponse)
async def search_logs(
    request: SearchRequest,
    llm_service=Depends(get_llm_service)
):
    """
    Direct semantic search in log embeddings
    
    This endpoint:
    1. Performs vector similarity search in Qdrant
    2. Returns matching logs with similarity scores
    3. No LLM processing - just raw search results
    """
    
    start_time = time.time()
    
    try:
        # Perform search using LLM service's search function
        results = llm_service.search_logs(
            query=request.query,
            limit=request.limit,
            time_filter=request.time_filter,
            service_filter=request.service_filter,
            level_filter=request.level_filter
        )
        
        # Convert results to response format
        log_entries = []
        for result in results:
            log = result.payload
            log_entries.append(LogEntry(
                service=log["service"],
                level=log["level"],
                message=log["message"],
                timestamp=log["timestamp"],
                similarity=round(result.score, 3)
            ))
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return SearchResponse(
            results=log_entries,
            total_found=len(results),
            query=request.query,
            filters_applied={
                "time": request.time_filter,
                "service": request.service_filter,
                "level": request.level_filter
            },
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )

@router.get("/services")
async def get_services(llm_service=Depends(get_llm_service)):
    """Get list of available services from logs"""
    
    try:
        # This is a simple implementation - in production you might want to cache this
        results = llm_service.search_logs("", limit=100)  # Get recent logs
        
        services = set()
        for result in results:
            services.add(result.payload["service"])
        
        return {"services": sorted(list(services))}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get services: {str(e)}"
        )