"""
Query endpoints for LLM-powered analysis
"""

import time
from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime

from ..models import QueryRequest, QueryResponse, LogEntry, ErrorResponse
from ..dependencies import get_llm_service

router = APIRouter(prefix="/query", tags=["query"])

@router.post("/", response_model=QueryResponse)
async def query_logs(
    request: QueryRequest,
    llm_service=Depends(get_llm_service)
):
    """
    Query logs using LLM with RAG (Retrieval Augmented Generation)
    
    This endpoint:
    1. Searches for relevant logs using semantic similarity
    2. Uses LLM to analyze and answer questions about the logs
    3. Returns structured response with context
    """
    
    start_time = time.time()
    
    try:
        # Call LLM service
        result = llm_service.query(
            question=request.question,
            limit=request.limit,
            time_filter=request.time_filter,
            service_filter=request.service_filter,
            level_filter=request.level_filter
        )
        
        # Convert context logs to response format
        context_logs = [
            LogEntry(
                service=log["service"],
                level=log["level"],
                message=log["message"],
                timestamp=log["timestamp"],
                similarity=log["similarity"]
            )
            for log in result["context_logs"]
        ]
        
        processing_time = int((time.time() - start_time) * 1000)
        
        return QueryResponse(
            answer=result["answer"],
            query_type=result["query_type"],
            logs_found=result["logs_found"],
            context_logs=context_logs,
            filters_applied=result["filters_applied"],
            processing_time_ms=processing_time
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )