#!/usr/bin/env python3

import time
import requests
import subprocess
import sys
import os
from qdrant_client import QdrantClient
from kafka import KafkaProducer
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_service(name, url, timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {name} is running")
            return True
    except:
        pass
    print(f"❌ {name} is not responding")
    return False

def check_kafka():
    try:
        producer = KafkaProducer(
            bootstrap_servers=['localhost:19092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        producer.send('test-topic', {'test': 'message'})
        producer.close()
        print("✅ Kafka is working")
        return True
    except:
        print("❌ Kafka connection failed")
        return False

def check_qdrant_data():
    try:
        client = QdrantClient(host="localhost", port=6333)
        collections = client.get_collections().collections
        
        if any(c.name == "logs" for c in collections):
            info = client.get_collection("logs")
            count = info.points_count
            print(f"✅ Qdrant has {count} log entries")
            return count > 0
        else:
            print("❌ No 'logs' collection in Qdrant")
            return False
    except Exception as e:
        print(f"❌ Qdrant check failed: {e}")
        return False

def run_producer(duration=30):
    print(f"\n🔄 Running log producer for {duration} seconds...")
    try:
        process = subprocess.Popen([
            sys.executable, "../producers/log-producer/producer.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(duration)
        process.terminate()
        process.wait()
        print("✅ Log producer completed")
        return True
    except Exception as e:
        print(f"❌ Producer failed: {e}")
        return False

def run_processor(duration=20):
    print(f"\n🔄 Running event processor for {duration} seconds...")
    try:
        process = subprocess.Popen([
            sys.executable, "../services/event-processor/processor.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        time.sleep(duration)
        process.terminate()
        process.wait()
        print("✅ Event processor completed")
        return True
    except Exception as e:
        print(f"❌ Processor failed: {e}")
        return False

def test_llm_service():
    print("\n🔄 Testing LLM service...")
    try:
        sys.path.append("../services/llm-service")
        from llm_service import LLMService
        
        service = LLMService()
        
        test_queries = [
            "What database errors are happening?",
            "Show me authentication failures",
            "Any performance issues?"
        ]
        
        results = []
        for query in test_queries:
            result = service.query(query, limit=3)
            results.append({
                "query": query,
                "logs_found": result["logs_found"],
                "has_answer": len(result["answer"]) > 50
            })
            print(f"  Query: '{query}' -> {result['logs_found']} logs, answer: {len(result['answer'])} chars")
        
        success = all(r["logs_found"] > 0 and r["has_answer"] for r in results)
        if success:
            print("✅ LLM service working correctly")
        else:
            print("❌ LLM service issues detected")
        return success
        
    except Exception as e:
        print(f"❌ LLM service test failed: {e}")
        return False

def main():
    print("=" * 60)
    print("OpenOps End-to-End Integration Test")
    print("=" * 60)
    
    print("\n1. Checking service health...")
    services_ok = all([
        check_service("Redpanda Console", "http://localhost:8080"),
        check_service("Qdrant", "http://localhost:6333"),
        check_service("Ollama", "http://localhost:11434"),
        check_kafka()
    ])
    
    if not services_ok:
        print("\n❌ Some services are down. Run 'docker-compose up -d' first.")
        return False
    
    print("\n2. Generating test data...")
    if not run_producer(30):
        return False
    
    print("\n3. Processing logs...")
    if not run_processor(20):
        return False
    
    print("\n4. Checking data pipeline...")
    time.sleep(5)
    if not check_qdrant_data():
        print("❌ No data found in Qdrant. Check event processor.")
        return False
    
    print("\n5. Testing LLM service...")
    if not test_llm_service():
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("OpenOps pipeline is working end-to-end")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)