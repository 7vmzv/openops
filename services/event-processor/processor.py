#!/usr/bin/env python3
"""
OpenOps Event Processor
Consumes logs from Kafka, generates embeddings, and stores in Qdrant
"""

import json
from datetime import datetime
from kafka import KafkaConsumer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

# Configuration
KAFKA_BROKER = "localhost:19092"
KAFKA_TOPIC = "logs.raw"
KAFKA_GROUP_ID = "event-processor"

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
QDRANT_COLLECTION = "logs"

# Embedding model (lightweight and fast)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # 384 dimensions


class EventProcessor:
    """Processes events from Kafka and stores in Qdrant"""
    
    def __init__(self):
        print("Initializing Event Processor...")
        
        # Initialize embedding model
        print(f"Loading embedding model: {EMBEDDING_MODEL}")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        print(f"Model loaded (dimension: {self.model.get_sentence_embedding_dimension()})")
        
        # Initialize Qdrant client
        print(f"Connecting to Qdrant at {QDRANT_HOST}:{QDRANT_PORT}")
        self.qdrant = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
        
        # Create collection if it doesn't exist
        self._setup_collection()
        
        # Initialize Kafka consumer
        print(f"Connecting to Kafka at {KAFKA_BROKER}")
        self.consumer = KafkaConsumer(
            KAFKA_TOPIC,
            bootstrap_servers=[KAFKA_BROKER],
            group_id=KAFKA_GROUP_ID,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',
            enable_auto_commit=True,
        )
        
        print("Initialization complete\n")
    
    def _setup_collection(self):
        """Create Qdrant collection if it doesn't exist"""
        collections = self.qdrant.get_collections().collections
        collection_names = [c.name for c in collections]
        
        if QDRANT_COLLECTION not in collection_names:
            print(f"Creating collection: {QDRANT_COLLECTION}")
            self.qdrant.create_collection(
                collection_name=QDRANT_COLLECTION,
                vectors_config=VectorParams(
                    size=self.model.get_sentence_embedding_dimension(),
                    distance=Distance.COSINE,
                ),
            )
            print(f"Collection created: {QDRANT_COLLECTION}")
        else:
            print(f"Collection already exists: {QDRANT_COLLECTION}")
    
    def process_log(self, log):
        """Process a single log entry"""
        # Create text for embedding (combine service, level, and message)
        text = f"[{log['level']}] {log['service']}: {log['message']}"
        
        # Generate embedding
        embedding = self.model.encode(text).tolist()
        
        # Create point for Qdrant
        point = PointStruct(
            id=hash(log['timestamp'] + log['service'] + log['message']) % (10 ** 10),
            vector=embedding,
            payload={
                "timestamp": log['timestamp'],
                "service": log['service'],
                "level": log['level'],
                "message": log['message'],
                "host": log['host'],
                "environment": log['environment'],
                "text": text,  # Store the full text for retrieval
            }
        )
        
        # Store in Qdrant
        self.qdrant.upsert(
            collection_name=QDRANT_COLLECTION,
            points=[point]
        )
        
        return point.id
    
    def run(self):
        """Main processing loop"""
        print(f"Consuming from topic: {KAFKA_TOPIC}")
        print(f"Storing embeddings in collection: {QDRANT_COLLECTION}")
        print("Processing logs... (Ctrl+C to stop)\n")
        
        count = 0
        try:
            for message in self.consumer:
                log = message.value
                
                # Process and store
                point_id = self.process_log(log)
                count += 1
                
                # Print progress every 10 logs
                if count % 10 == 0:
                    print(f"Processed {count} logs | Last: [{log['level']}] {log['service']}: {log['message'][:50]}...")
                
        except KeyboardInterrupt:
            print(f"\n\nStopping processor... (processed {count} logs)")
            self.consumer.close()
            print("Processor stopped cleanly")


def main():
    """Entry point"""
    print("=" * 60)
    print("OpenOps Event Processor")
    print("=" * 60)
    print()
    
    processor = EventProcessor()
    processor.run()


if __name__ == "__main__":
    main()
