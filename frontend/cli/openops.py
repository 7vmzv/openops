#!/usr/bin/env python3
"""
OpenOps CLI - Simple command-line interface for OpenOps
"""

import requests
import json
import sys
import argparse
from datetime import datetime
from typing import Optional

API_BASE = "http://localhost:8000"

class OpenOpsCLI:
    def __init__(self, api_base: str = API_BASE):
        self.api_base = api_base
    
    def _make_request(self, method: str, endpoint: str, data: dict = None) -> dict:
        """Make HTTP request to API"""
        url = f"{self.api_base}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"API Error ({response.status_code}): {response.text}")
                return None
                
        except requests.exceptions.ConnectionError:
            print(f"ERROR: Cannot connect to OpenOps API at {self.api_base}")
            print("       Make sure the API Gateway is running!")
            return None
        except requests.exceptions.Timeout:
            print("ERROR: Request timeout - API may be overloaded")
            return None
        except Exception as e:
            print(f"ERROR: Unexpected error: {e}")
            return None
    
    def health(self):
        """Check system health"""
        print("Checking OpenOps system health...")
        
        result = self._make_request("GET", "/health/")
        if not result:
            return
        
        status = result["status"]
        status_indicator = "OK" if status == "healthy" else "WARN"
        
        print(f"System Status: {status.upper()} [{status_indicator}]")
        print(f"Timestamp: {result['timestamp']}")
        print(f"Version: {result['version']}")
        print("\nServices:")
        
        for service, status in result["services"].items():
            status_indicator = "OK" if "healthy" in status else "FAIL"
            print(f"  {service}: {status} [{status_indicator}]")
    
    def query(self, question: str, limit: int = 5, time_filter: str = None, 
              service_filter: str = None, level_filter: str = None):
        """Query logs using LLM"""
        print(f"Query: {question}")
        
        payload = {
            "question": question,
            "limit": limit
        }
        
        if time_filter:
            payload["time_filter"] = time_filter
        if service_filter:
            payload["service_filter"] = service_filter
        if level_filter:
            payload["level_filter"] = level_filter
        
        result = self._make_request("POST", "/query/", payload)
        if not result:
            return
        
        print(f"\nAnswer ({result['query_type']} query):")
        print(f"{result['answer']}")
        
        print(f"\nFound {result['logs_found']} relevant logs ({result['processing_time_ms']}ms)")
        
        if result['context_logs']:
            print("\nContext logs:")
            for i, log in enumerate(result['context_logs'], 1):
                similarity = f"({log['similarity']:.2f})" if log['similarity'] else ""
                print(f"  {i}. [{log['level']}] {log['service']}: {log['message'][:80]}... {similarity}")
    
    def search(self, query: str, limit: int = 10, time_filter: str = None,
               service_filter: str = None, level_filter: str = None):
        """Search logs directly"""
        print(f"Searching logs for: {query}")
        
        payload = {
            "query": query,
            "limit": limit
        }
        
        if time_filter:
            payload["time_filter"] = time_filter
        if service_filter:
            payload["service_filter"] = service_filter
        if level_filter:
            payload["level_filter"] = level_filter
        
        result = self._make_request("POST", "/search/", payload)
        if not result:
            return
        
        print(f"\nFound {result['total_found']} matching logs ({result['processing_time_ms']}ms)")
        
        if result['results']:
            print("\nResults:")
            for i, log in enumerate(result['results'], 1):
                similarity = f"({log['similarity']:.2f})" if log['similarity'] else ""
                timestamp = log['timestamp'][:19].replace('T', ' ')
                print(f"  {i}. [{log['level']}] {log['service']} | {timestamp}")
                print(f"     {log['message']} {similarity}")
                print()
    
    def services(self):
        """List available services"""
        print("Getting available services...")
        
        result = self._make_request("GET", "/search/services")
        if not result:
            return
        
        services = result.get("services", [])
        print(f"\nAvailable services ({len(services)}):")
        for service in services:
            print(f"  - {service}")

def main():
    parser = argparse.ArgumentParser(
        description="OpenOps CLI - AI-powered DevOps assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  openops health
  openops query "What database errors happened?"
  openops query "Show me payment service issues" --service payment-service --time 1h
  openops search "timeout" --limit 5
  openops services
        """
    )
    
    parser.add_argument("--api", default=API_BASE, help="API Gateway URL")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Health command
    subparsers.add_parser("health", help="Check system health")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Ask questions about logs")
    query_parser.add_argument("question", help="Question to ask")
    query_parser.add_argument("--limit", type=int, default=5, help="Max logs to analyze")
    query_parser.add_argument("--time", help="Time filter: 1h, 24h, 7d")
    query_parser.add_argument("--service", help="Filter by service")
    query_parser.add_argument("--level", help="Filter by log level")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search logs directly")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--limit", type=int, default=10, help="Max results")
    search_parser.add_argument("--time", help="Time filter: 1h, 24h, 7d")
    search_parser.add_argument("--service", help="Filter by service")
    search_parser.add_argument("--level", help="Filter by log level")
    
    # Services command
    subparsers.add_parser("services", help="List available services")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Create CLI instance
    cli = OpenOpsCLI(args.api)
    
    # Print header
    print("=" * 60)
    print("OpenOps CLI - AI DevOps Assistant")
    print("=" * 60)
    
    # Execute command
    if args.command == "health":
        cli.health()
    
    elif args.command == "query":
        cli.query(
            question=args.question,
            limit=args.limit,
            time_filter=args.time,
            service_filter=args.service,
            level_filter=args.level
        )
    
    elif args.command == "search":
        cli.search(
            query=args.query,
            limit=args.limit,
            time_filter=args.time,
            service_filter=args.service,
            level_filter=args.level
        )
    
    elif args.command == "services":
        cli.services()

if __name__ == "__main__":
    main()