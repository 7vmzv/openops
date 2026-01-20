#!/usr/bin/env python3

import json
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
import psycopg2
from psycopg2.extras import RealDictCursor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
TIMESCALE_HOST = "localhost"
TIMESCALE_PORT = 5432
TIMESCALE_DB = "openops"
TIMESCALE_USER = "openops"
TIMESCALE_PASSWORD = "openops123"


class SimpleMetricsService:
    """Lightweight metrics service for LLM integration"""
    
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                host=TIMESCALE_HOST,
                port=TIMESCALE_PORT,
                database=TIMESCALE_DB,
                user=TIMESCALE_USER,
                password=TIMESCALE_PASSWORD,
                cursor_factory=RealDictCursor
            )
        except Exception as e:
            logger.error(f"Failed to connect to TimescaleDB: {e}")
            self.conn = None
    
    def get_error_rate(self, service: str, hours: int = 1) -> float:
        if not self.conn:
            return 0.0
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        COALESCE(SUM(error_count), 0) as total_errors,
                        COALESCE(SUM(log_count), 0) as total_logs
                    FROM log_metrics 
                    WHERE service = %s 
                    AND time > NOW() - INTERVAL '%s hours'
                """, (service, hours))
                
                result = cursor.fetchone()
                if result['total_logs'] == 0:
                    return 0.0
                
                return (result['total_errors'] / result['total_logs']) * 100
        except Exception as e:
            logger.error(f"Error getting error rate: {e}")
            return 0.0
    
    def get_service_summary(self, hours: int = 1) -> List[dict]:
        if not self.conn:
            return []
        
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        service,
                        SUM(log_count) as total_logs,
                        SUM(error_count) as total_errors,
                        CASE 
                            WHEN SUM(log_count) > 0 
                            THEN (SUM(error_count)::float / SUM(log_count)) * 100 
                            ELSE 0 
                        END as error_rate
                    FROM log_metrics 
                    WHERE time > NOW() - INTERVAL '%s hours'
                    GROUP BY service
                    ORDER BY error_rate DESC
                """, (hours,))
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting service summary: {e}")
            return []
    
    def detect_spike(self, service: str, threshold: float = 2.0) -> Optional[dict]:
        """Detect if current error rate is a spike"""
        if not self.conn:
            return None
        
        try:
            # Get current rate (last 10 minutes)
            current_rate = self.get_error_rate(service, hours=0.17)
            
            # Get baseline (last 24 hours, excluding recent)
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    SELECT AVG(
                        CASE 
                            WHEN log_count > 0 
                            THEN (error_count::float / log_count) * 100 
                            ELSE 0 
                        END
                    ) as baseline_rate
                    FROM log_metrics 
                    WHERE service = %s 
                    AND time > NOW() - INTERVAL '24 hours'
                    AND time < NOW() - INTERVAL '1 hour'
                """, (service,))
                
                result = cursor.fetchone()
                baseline_rate = result['baseline_rate'] or 0.0
            
            if baseline_rate == 0 or current_rate == 0:
                return None
            
            spike_ratio = current_rate / baseline_rate
            
            if spike_ratio >= threshold:
                return {
                    'service': service,
                    'current_rate': current_rate,
                    'baseline_rate': baseline_rate,
                    'spike_ratio': spike_ratio,
                    'severity': 'HIGH' if spike_ratio >= 5 else 'MEDIUM'
                }
            
            return None
        except Exception as e:
            logger.error(f"Error detecting spike for {service}: {e}")
            return None

class LLMService:
    def __init__(self, ollama_host="localhost:11434", qdrant_host="localhost", qdrant_port=6333):
        logger.info("Initializing LLM Service...")
        
        self.ollama_url = f"http://{ollama_host}/api/generate"
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.qdrant = QdrantClient(host=qdrant_host, port=qdrant_port)
        
        self.metrics = SimpleMetricsService()
        
        self.query_patterns = {
            'error_analysis': ['error', 'fail', 'exception', 'crash', 'bug'],
            'performance': ['slow', 'timeout', 'latency', 'performance', 'response time'],
            'security': ['auth', 'login', 'permission', 'unauthorized', 'security'],
            'deployment': ['deploy', 'release', 'version', 'rollback'],
            'summary': ['summary', 'overview', 'what happened', 'status'],
            'anomaly': ['unusual', 'pattern', 'spike', 'anomaly', 'baseline', 'abnormal'],
            'metrics': ['rate', 'trend', 'metric', 'performance']
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
    
    def _build_context(self, results: List, query_type: str, service_filter: Optional[str] = None) -> str:
        if not results:
            return "No relevant logs found."
        
        context = "Recent logs:\n"
        
        for i, result in enumerate(results, 1):
            log = result.payload
            context += f"{i}. [{log['level']}] {log['service']}: {log['message'][:80]}...\n"
        
        # Add metrics context if available
        if service_filter:
            metrics_context = self._get_metrics_context(service_filter)
            if metrics_context:
                context += f"\nMetrics for {service_filter}:\n{metrics_context}"
        else:
            # Get summary for all services
            summary_context = self._get_summary_metrics()
            if summary_context:
                context += f"\nSystem metrics:\n{summary_context}"
        
        return context
    
    def _get_metrics_context(self, service: str) -> str:
        """Get metrics context for a specific service"""
        try:
            error_rate = self.metrics.get_error_rate(service, hours=1)
            spike = self.metrics.detect_spike(service)
            
            context = f"Error rate (last hour): {error_rate:.1f}%"
            
            if spike:
                context += f"\n🚨 SPIKE DETECTED: {spike['spike_ratio']:.1f}x baseline ({spike['severity']})"
            
            return context
        except Exception as e:
            logger.error(f"Error getting metrics for {service}: {e}")
            return ""
    
    def _get_summary_metrics(self) -> str:
        """Get summary metrics for all services"""
        try:
            summary = self.metrics.get_service_summary(hours=1)
            if not summary:
                return ""
            
            context = "Service error rates (last hour):\n"
            anomalies = []
            
            for service in summary[:5]:  # Top 5 services
                context += f"  {service['service']}: {service['error_rate']:.1f}% ({service['total_logs']} logs)\n"
                
                # Check for spikes
                spike = self.metrics.detect_spike(service['service'])
                if spike:
                    anomalies.append(f"🚨 {service['service']}: {spike['spike_ratio']:.1f}x baseline ({spike['severity']})")
            
            if anomalies:
                context += "\nAnomalies detected:\n"
                for anomaly in anomalies:
                    context += f"  {anomaly}\n"
            
            return context
        except Exception as e:
            logger.error(f"Error getting summary metrics: {e}")
            return ""
    
    def _get_prompt_template(self, query_type: str, context: str, question: str) -> str:
        return f"""You are a DevOps expert analyzing system logs and metrics. Answer briefly and focus on actionable insights.

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
            
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            
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
        
        context = self._build_context(results, query_type, service_filter)
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