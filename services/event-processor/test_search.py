#!/usr/bin/env python3
"""
Test semantic search on stored logs
"""

from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Configuration
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_COLLECTION = "logs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

def search_logs(query, limit=5):
    """Search for logs semantically similar to the query"""
    
    print(f"\nSearching for: '{query}'")
    print("=" * 60)
    
    # Initialize
    model = SentenceTransformer(EMBEDDING_MODEL)
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    
    # Generate query vector
    query_vector = model.encode(query).tolist()
    
    # Search
    results = client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_vector,
        limit=limit
    )
    
    # Display results
    if not results:
        print("No results found")
        return
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Similarity: {result.score:.3f}")
        print(f"   Service: {result.payload['service']}")
        print(f"   Level: {result.payload['level']}")
        print(f"   Message: {result.payload['message']}")
        print(f"   Time: {result.payload['timestamp']}")

def main():
    """Run example searches"""
    
    print("=" * 60)
    print("OpenOps Semantic Log Search")
    print("=" * 60)
    
    # Example searches
    queries = [
        "database connection problems",
        "payment failures",
        "authentication errors",
        "slow performance",
    ]
    
    for query in queries:
        search_logs(query, limit=3)
        print()
    
    # Interactive mode
    print("\n" + "=" * 60)
    print("Interactive Search (Ctrl+C to exit)")
    print("=" * 60)
    
    try:
        while True:
            query = input("\nEnter search query: ").strip()
            if query:
                search_logs(query, limit=5)
    except KeyboardInterrupt:
        print("\n\nExiting...")

if __name__ == "__main__":
    main()
