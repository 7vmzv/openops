# OpenOps Copilot

An AI-powered DevOps assistant that observes your systems, detects anomalies, and answers questions about your infrastructure.

## What It Does

Ask questions like:
- "What caused the spike in errors today?"
- "What was deployed in the last hour?"
- "Show me anomalies in service X"
- "Why is latency increasing on the API gateway?"

##  Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

**Tech Stack:**
- **Redpanda** (Kafka-compatible message broker)
- **Qdrant** (vector database for log embeddings)
- **TimescaleDB** (time-series metrics)
- **Ollama** (local LLM)
- **FastAPI** (API gateway)

## Quick Start

### 1. Start Infrastructure

```bash
cd infra
docker-compose up -d
```

Wait ~30 seconds, then verify:
```bash
docker-compose ps
```

### 2. Access Services

- **Redpanda Console**: http://localhost:8080
- **Qdrant Dashboard**: http://localhost:6333/dashboard

### 3. Test Redpanda

```bash
# Create a test topic
docker exec -it openops-redpanda rpk topic create test-topic

# Produce a message
echo "Hello OpenOps" | docker exec -i openops-redpanda rpk topic produce test-topic

# View in console: http://localhost:8080
```

## Development Roadmap

See [ROADMAP.md](ROADMAP.md) for detailed phases.

**Current Status:** Phase 1 - Core Pipeline

## Project Structure

```
openops/
├── infra/              # Docker Compose, configs
├── services/           # Microservices (event-processor, llm-service, api-gateway)
├── producers/          # Test data producers
├── shared/             # Common code, schemas
├── frontend/           # CLI and web UI
├── tests/              # Tests
└── docs/               # Documentation
```

# Development

### Prerequisites
- Docker Desktop
- Python 3.11+
- 4GB+ RAM for Docker

### Next Steps
1. Setup Redpanda (Done)
2. Create log producer
3. Build event processor
4. Add LLM service

## License

TBD (Apache 2.0 or MIT)

## Contributing

Coming soon! This project is in active development.

---