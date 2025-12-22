#!/usr/bin/env python3

import json
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, ollama_host="localhost:11434", qdrant_host="localhost", qdrant_port=6333):
        logger.info("Initializing LLM Service...")
        
        self.ollama_url = f"http://{ollama_host}/api/generate"
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.qdrant = QdrantClient(host=qdrant_host, port=qdrant_port)
        
        self.query_patterns = {
            'error_analysis': ['error', 'fail', 'exception', 'crash', 'bug'],
            'performance': ['slow', 'timeout', 'latency', 'performance', 'response time'],
            'security': ['auth', 'login', 'permission', 'unauthorized', 'security'],
            'deployment': ['deploy', 'release', 'version', 'rollback'],
            'summary': ['summary', 'overview', 'what happened', 'status']
        }
        
        logger.info("LLM Service initialized")
    
    def _detect_query_type(self, question: str) -> str:
        question_lower = question.lower()
        
        for query_type, keywords in self.query_patterns.items():
            if any(keyword in question_lower for keyword in keywords):
                return query_type
        
        return 'general'
    
    def search_logs(self, query: str, limit: int = 5, time_filter: Optional[str] = None, 
                   service_filter: Optional[str] = None, level_filter: Optional[str] = None) -> List:
        try:
            vector = self.model.encode(query).tolist()
            
            filters = []
            
            if time_filter:
                hours = {'1h': 1, '24h': 24, '7d': 168}.get(time_filter, 24)
                cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat() + "Z"
                filters.append(FieldCondition(key="timestamp", range={"gte": cutoff}))
            
            if service_filter:
                filters.append(FieldCondition(key="service", match=MatchValue(value=service_filter)))
            
            if level_filter:
                filters.append(FieldCondition(key="level", match=MatchValue(value=level_filter)))
            
            search_filter = Filter(must=filters) if filters else None
            
            results = self.qdrant.search(
                collection_name="logs",
                query_vector=vector,
                limit=limit,
                query_filter=search_filter
            )
            
            logger.info(f"Found {len(results)} relevant logs for query: {query[:50]}...")
            
            for i, result in enumerate(results, 1):
                log = result.payload
                logger.info(f"  Log {i}: [{log['level']}] {log['service']}: {log['message'][:100]}... (score: {result.score:.3f})")
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching logs: {e}")
            return []
    
    def _build_context(self, results: List, query_type: str) -> str:
        if not results:
            return "No relevant logs found."
        
        context = "Recent logs:\n"
        
        for i, result in enumerate(results, 1):
            log = result.payload
            context += f"{i}. [{log['level']}] {log['service']}: {log['message'][:80]}...\n"
        
        return context
    
    def _get_prompt_template(self, query_type: str, context: str, question: str) -> str:
        return f"""You are a DevOps expert. Answer briefly.

{context}

Question: {question}
Answer:"""
    
    def ask_llm(self, prompt: str, max_tokens: int = 500) -> str:
        try:
            payload = {
                "model": "llama3.2:1b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 100,
                    "temperature": 0.3
                }
            }
            
            logger.info("Sending request to Ollama...")
            logger.info(f"Prompt length: {len(prompt)} chars")
            logger.info(f"Prompt preview: {prompt[:200]}...")
            
            response = requests.post(self.ollama_url, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                answer = result.get("response", "No response from LLM")
                logger.info(f"Ollama response: {answer}")
                return answer
            else:
                logger.error(f"Ollama error: {response.status_code} - {response.text}")
                return f"LLM service error: {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error("Ollama request timeout")
            return "Request timeout - LLM service may be overloaded"
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama")
            return "Cannot connect to LLM service - is Ollama running?"
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return f"Unexpected error: {str(e)}"
    
    def query(self, question: str, limit: int = 5, time_filter: Optional[str] = None,
             service_filter: Optional[str] = None, level_filter: Optional[str] = None) -> Dict:
        logger.info(f"Processing query: {question}")
        
        query_type = self._detect_query_type(question)
        logger.info(f"Detected query type: {query_type}")
        
        results = self.search_logs(question, limit, time_filter, service_filter, level_filter)
        
        if not results:
            return {
                "answer": "No relevant logs found for your query.",
                "query_type": query_type,
                "logs_found": 0,
                "filters_applied": {
                    "time": time_filter,
                    "service": service_filter,
                    "level": level_filter
                }
            }
        
        context = self._build_context(results, query_type)
        prompt = self._get_prompt_template(query_type, context, question)
        
        answer = self.ask_llm(prompt)
        
        return {
            "answer": answer,
            "query_type": query_type,
            "logs_found": len(results),
            "context_logs": [
                {
                    "service": r.payload["service"],
                    "level": r.payload["level"],
                    "message": r.payload["message"][:100] + "..." if len(r.payload["message"]) > 100 else r.payload["message"],
                    "timestamp": r.payload["timestamp"],
                    "similarity": round(r.score, 3)
                } for r in results
            ],
            "filters_applied": {
                "time": time_filter,
                "service": service_filter,
                "level": level_filter
            }
        }

def main():
    service = LLMService()
    
    test_queries = [
        "What database errors are happening?",
        "Show me performance issues in the last hour",
        "Any authentication failures?",
        "Summarize system status"
    ]
    
    print("=" * 60)
    print("OpenOps Enhanced LLM Service Test")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 40)
        
        result = service.query(query, limit=3)
        print(f"Answer: {result['answer']}")
        print(f"Query Type: {result['query_type']}")
        print(f"Logs Found: {result['logs_found']}")
        
        if result['context_logs']:
            print("\nRelevant Logs:")
            for i, log in enumerate(result['context_logs'], 1):
                print(f"  {i}. [{log['level']}] {log['service']}: {log['message']} (sim: {log['similarity']})")
        
        print("\n" + "=" * 60)

if __name__ == "__main__":
    main()