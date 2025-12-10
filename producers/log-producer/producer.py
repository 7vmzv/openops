#!/usr/bin/env python3
"""
OpenOps Log Producer
Generates fake application logs and sends them to Redpanda/Kafka
"""

import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer
from faker import Faker

# Initialize
fake = Faker()

# Configuration
KAFKA_BROKER = "localhost:19092"
TOPIC = "logs.raw"
LOGS_PER_SECOND = 10

# Services in our fake infrastructure
SERVICES = [
    "api-gateway",
    "auth-service",
    "payment-service",
    "user-service",
    "notification-service",
    "database-proxy",
]

# Log levels with weights (more INFO, fewer CRITICAL)
LOG_LEVELS = ["INFO", "INFO", "INFO", "WARNING", "WARNING", "ERROR", "CRITICAL"]

# Log message templates
LOG_TEMPLATES = {
    "INFO": [
        "Request processed successfully: {} {} - {}ms",
        "User {} logged in from {}",
        "Cache hit for key: {}",
        "Database query executed in {}ms",
        "Message published to queue: {}",
    ],
    "WARNING": [
        "Slow query detected: {}ms",
        "Rate limit approaching for user {}",
        "Retry attempt {} for operation {}",
        "Cache miss for key: {}",
    ],
    "ERROR": [
        "Database connection timeout after {}ms",
        "Failed to process payment for order {}",
        "Authentication failed for user {}",
        "API request failed: {} - status {}",
        "Message queue connection lost",
    ],
    "CRITICAL": [
        "Database connection pool exhausted",
        "Service {} is not responding",
        "Out of memory error",
        "Disk space critically low: {}% remaining",
    ],
}


def generate_log():
    """Generate a single fake log entry"""
    service = random.choice(SERVICES)
    level = random.choice(LOG_LEVELS)
    template = random.choice(LOG_TEMPLATES[level])
    
    # Fill template with fake data
    if "Request processed" in template:
        message = template.format(
            random.choice(["GET", "POST", "PUT", "DELETE"]),
            fake.uri_path(),
            random.randint(10, 500)
        )
    elif "User" in template and "logged in" in template:
        message = template.format(fake.user_name(), fake.ipv4())
    elif "Retry attempt" in template:
        message = template.format(random.randint(1, 5), fake.word())
    elif "Service" in template and "not responding" in template:
        message = template.format(random.choice(SERVICES))
    elif "status" in template:
        message = template.format(
            fake.uri_path(),
            random.choice([400, 401, 403, 404, 500, 502, 503])
        )
    elif "order" in template:
        message = template.format(fake.uuid4())
    elif "%" in template:
        message = template.format(random.randint(1, 10))
    elif "{}" in template:
        # Generic single placeholder
        if "ms" in template:
            message = template.format(random.randint(100, 5000))
        else:
            message = template.format(fake.word())
    else:
        message = template
    
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": service,
        "level": level,
        "message": message,
        "host": f"{service}-{random.randint(1, 5)}",
        "environment": "production",
    }


def main():
    """Main producer loop"""
    print(f"Starting OpenOps Log Producer")
    print(f"Kafka Broker: {KAFKA_BROKER}")
    print(f"Topic: {TOPIC}")
    print(f"Rate: {LOGS_PER_SECOND} logs/second")
    print()
    
    # Create Kafka producer
    producer = KafkaProducer(
        bootstrap_servers=[KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        compression_type='gzip',
    )
    
    print("Connected to Kafka")
    print("Producing logs... (Ctrl+C to stop)")
    print()
    
    count = 0
    try:
        while True:
            log = generate_log()
            producer.send(TOPIC, value=log)
            count += 1
            
            # Print progress every 10 logs
            if count % 10 == 0:
                print(f"Sent {count} logs | Last: [{log['level']}] {log['service']}: {log['message'][:60]}...")
            
            # Sleep to maintain rate
            time.sleep(1.0 / LOGS_PER_SECOND)
            
    except KeyboardInterrupt:
        print(f"\n\nStopping producer... (sent {count} logs)")
        producer.flush()
        producer.close()
        print("Producer stopped cleanly")


if __name__ == "__main__":
    main()
