#!/usr/bin/env python3
"""
Test script for OpenOps API Gateway
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("=== Testing Health Endpoint ===")
    
    try:
        response = requests.get(f"{API_BASE}/health/")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()

def test_search():
    """Test search endpoint"""
    print("=== Testing Search Endpoint ===")
    
    payload = {
        "query": "database error",
        "limit": 3
    }
    
    try:
        response = requests.post(f"{API_BASE}/search/", json=payload)
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Found: {result['total_found']} logs")
        print(f"Processing time: {result['processing_time_ms']}ms")
        
        for i, log in enumerate(result['results'], 1):
            print(f"  {i}. [{log['level']}] {log['service']}: {log['message'][:60]}... (sim: {log['similarity']})")
    
    except Exception as e:
        print(f"Error: {e}")
    
    print()

def test_query():
    """Test query endpoint"""
    print("=== Testing Query Endpoint ===")
    
    payload = {
        "question": "What database errors are happening?",
        "limit": 3
    }
    
    try:
        response = requests.post(f"{API_BASE}/query/", json=payload)
        print(f"Status: {response.status_code}")
        result = response.json()
        
        print(f"Query type: {result['query_type']}")
        print(f"Logs found: {result['logs_found']}")
        print(f"Processing time: {result['processing_time_ms']}ms")
        print(f"Answer: {result['answer'][:200]}...")
        
        print("\nContext logs:")
        for i, log in enumerate(result['context_logs'], 1):
            print(f"  {i}. [{log['level']}] {log['service']}: {log['message'][:60]}...")
    
    except Exception as e:
        print(f"Error: {e}")
    
    print()

def test_services():
    """Test services endpoint"""
    print("=== Testing Services Endpoint ===")
    
    try:
        response = requests.get(f"{API_BASE}/search/services")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Available services: {result['services']}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    print()

def main():
    """Run all tests"""
    print("OpenOps API Gateway Test Suite")
    print("=" * 50)
    print(f"Testing API at: {API_BASE}")
    print()
    
    # Wait a moment for server to be ready
    print("Waiting for server...")
    time.sleep(2)
    
    # Run tests
    test_health()
    test_search()
    test_query()
    test_services()
    
    print("Test suite completed!")

if __name__ == "__main__":
    main()