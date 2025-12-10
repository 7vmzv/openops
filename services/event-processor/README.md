# Event Processor

Consumes logs from Kafka, generates embeddings, and stores them in Qdrant for semantic search.

## What It Does

1. **Consumes** logs from Kafka topic `logs.raw`
2. **Generates embeddings** using sentence-transformers (all-MiniLM-L6-v2)
3. **Stores** embeddings + metadata in Qdrant vector database

## Architecture

```
Kafka (logs.raw)
    |
    v
Event Processor
    |
    +---> Sentence Transformer (embedding generation)
    |
    v
Qdrant (vector storage)
```

## Quick Start

### 1. Install Dependencies

```bash
cd services/event-processor
pip install -r requirements.txt
```

Note: First run will download the embedding model (~80MB).

### 2. Run Processor

```bash
python processor.py
```

You should see:
```
============================================================
OpenOps Event Processor
============================================================

Initializing Event Processor...
Loading embedding model: all-MiniLM-L6-v2
Model loaded (dimension: 384)
Connecting to Qdrant at localhost:6333
Creating collection: logs
Collection created: logs
Connecting to Kafka at localhost:19092
Initialization complete

Consuming from topic: logs.raw
Storing embeddings in collection: logs
Processing logs... (Ctrl+C to stop)

Processed 10 logs | Last: [INFO] api-gateway: Request processed...
Processed 20 logs | Last: [ERROR] payment-service: Failed to process...
```

### 3. Verify in Qdrant

Open http://localhost:6333/dashboard

- You should see collection `logs`
- Click on it to see stored vectors and metadata

## Configuration

Edit `processor.py` to customize:

```python
KAFKA_BROKER = "localhost:19092"
KAFKA_TOPIC = "logs.raw"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_COLLECTION = "logs"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384 dimensions
```

## Embedding Model

**all-MiniLM-L6-v2**:
- Size: ~80MB
- Dimensions: 384
- Speed: ~14,000 sentences/sec (CPU)
- Quality: Good for semantic search

Alternative models:
- `all-mpnet-base-v2` (768 dim, better quality, slower)
- `paraphrase-MiniLM-L3-v2` (384 dim, faster, lower quality)

## Data Format in Qdrant

Each log is stored as:
```json
{
  "id": 1234567890,
  "vector": [0.123, -0.456, ...],  // 384 dimensions
  "payload": {
    "timestamp": "2025-01-09T10:30:45.123456Z",
    "service": "api-gateway",
    "level": "ERROR",
    "message": "Database connection timeout after 3000ms",
    "host": "api-gateway-3",
    "environment": "production",
    "text": "[ERROR] api-gateway: Database connection timeout..."
  }
}
```

## Testing

Once running, you can search for similar logs:

```python
from qdrant_client import QdrantClient

client = QdrantClient(host="localhost", port=6333)

# Search for logs similar to "database timeout"
results = client.search(
    collection_name="logs",
    query_vector=model.encode("database timeout error").tolist(),
    limit=5
)

for result in results:
    print(f"Score: {result.score}")
    print(f"Log: {result.payload['text']}")
```

## Stop Processor

Press `Ctrl+C` to stop gracefully.
