#!/usr/bin/env python3
"""
Simple LLM Service with RAG
"""

import requests
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

class LLMService:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.qdrant = QdrantClient(host="localhost", port=6333)
    
    def search_logs(self, query, limit=5):
        """Find relevant logs"""
        vector = self.model.encode(query).tolist()
        return self.qdrant.search(
            collection_name="logs",
            query_vector=vector,
            limit=limit
        )
    
    def ask_llm(self, prompt):
        """Get response from Ollama"""
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "llama3.2:1b", "prompt": prompt, "stream": False}
        )
        return response.json()["response"] if response.status_code == 200 else "Error"
    
    def query(self, question):
        """Main RAG function"""
        # Get relevant logs
        results = self.search_logs(question, limit=3)
        
        if not results:
            return "No relevant logs found"
        
        # Build context
        context = "Recent logs:\n"
        for i, result in enumerate(results, 1):
            log = result.payload
            context += f"{i}. [{log['level']}] {log['service']}: {log['message']}\n"
        
        # Create prompt
        prompt = f"""You are a DevOps expert. Analyze these logs and answer the question.

{context}

Question: {question}

Answer briefly and clearly:"""
        
        return self.ask_llm(prompt)

if __name__ == "__main__":
    service = LLMService()
    
    # Test
    response = service.query("What database errors are happening?")
    print(response)