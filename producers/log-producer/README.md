# Log Producer

Generates fake application logs and sends them to Redpanda/Kafka.

## 🎯 What It Does

Simulates logs from multiple services:
- `api-gateway`
- `auth-service`
- `payment-service`
- `user-service`
- `notification-service`
- `database-proxy`

With realistic log levels and messages:
- **INFO**: Normal operations (HTTP requests, logins, cache hits)
- **WARNING**: Slow queries, rate limits, retries
- **ERROR**: Connection timeouts, failed payments, auth failures
- **CRITICAL**: Service outages, out of memory, disk full

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd producers/log-producer
pip install -r requirements.txt
```

### 2. Run Producer

```bash
python producer.py
```

You should see:
```
🚀 Starting OpenOps Log Producer
📡 Kafka Broker: localhost:19092
📝 Topic: logs.raw
⚡ Rate: 10 logs/second

✅ Connected to Kafka
📤 Producing logs... (Ctrl+C to stop)

✓ Sent 10 logs | Last: [INFO] api-gateway: Request processed successfully...
✓ Sent 20 logs | Last: [ERROR] payment-service: Failed to process payment...
```

### 3. Verify Logs in Redpanda

```bash
# View logs in console
docker exec -it openops-redpanda rpk topic consume logs.raw --num 5
```

Or open http://localhost:8080 → Topics → `logs.raw`

## ⚙️ Configuration

Edit `producer.py` to customize:

```python
KAFKA_BROKER = "localhost:19092"  # Kafka address
TOPIC = "logs.raw"                # Topic name
LOGS_PER_SECOND = 10              # Production rate
```

## 📊 Sample Log Format

```json
{
  "timestamp": "2025-01-09T10:30:45.123456Z",
  "service": "api-gateway",
  "level": "ERROR",
  "message": "Database connection timeout after 3000ms",
  "host": "api-gateway-3",
  "environment": "production"
}
```

## 🛑 Stop Producer

Press `Ctrl+C` to stop gracefully.
