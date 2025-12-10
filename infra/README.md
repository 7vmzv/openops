# OpenOps Infrastructure

This directory contains Docker Compose setup for all infrastructure component Quick Start

### Prerequisites
- Docker Desktop installed and running
- At least 4GB RAM available for Docker

### Start All Services

```bash
cd infra
docker-compose up -d
```

### Check Service Health

```bash
docker-compose ps
```

You should see:
- `openops-redpanda` (healthy)
- `openops-console` (running)
- `openops-qdrant` (running)

### Access Services

| Service | URL | Purpose |
|---------|-----|---------|
| Redpanda Console | http://localhost:8080 | View topics, messages, schemas |
| Qdrant Dashboard | http://localhost:6333/dashboard | View vector collections |
| Redpanda Kafka API | localhost:19092 | Connect producers/consumers |

## Test Redpanda

### Using rpk (Redpanda CLI inside container)

```bash
# Create a test topic
docker exec -it openops-redpanda rpk topic create test-topic

# List topics
docker exec -it openops-redpanda rpk topic list

# Produce a message
echo "Hello OpenOps" | docker exec -i openops-redpanda rpk topic produce test-topic

# Consume messages
docker exec -it openops-redpanda rpk topic consume test-topic
```

### Using Redpanda Console (Web UI)

1. Open http://localhost:8080
2. Go to "Topics"
3. You should see `test-topic` (if you created it above)
4. Click on it to view messages

## Stop Services

```bash
docker-compose down
```

To also remove volumes (data):
```bash
docker-compose down -v
```

## Default Topics (Auto-Created)

These topics will be created automatically by our services:
- `logs.raw` - Application logs
- `metrics.raw` - System metrics
- `deployments` - CI/CD deployment events
- `alerts.raw` - Alert notifications
- `insights` - Processed insights and anomalies

## Troubleshooting

### Redpanda won't start
- Check Docker has enough memory (4GB minimum)
- Check ports 19092, 8080, 6333 are not in use

### Can't connect to Kafka
- Use `localhost:19092` from your host machine
- Use `redpanda:9092` from inside Docker network

### Qdrant connection issues
- Verify it's running: `docker logs openops-qdrant`
- Check http://localhost:6333/dashboard
