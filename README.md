# OpenOps Copilot

An AI-powered DevOps assistant that observes your systems, detects anomalies, and answers questions about your infrastructure using natural language.

## What It Does

Ask questions like:
- "What database errors happened in the last hour?"
- "Show me authentication failures"
- "Explain these error patterns"
- "Why is the payment service having issues?"

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

**Tech Stack:**
- **Redpanda** (Kafka-compatible message broker)
- **Qdrant** (vector database for log embeddings)
- **Ollama** (local LLM with llama3.2:1b)
- **FastAPI** (API gateway)
- **sentence-transformers** (all-MiniLM-L6-v2 for embeddings)

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
- **Ollama API**: http://localhost:11434

### 3. Generate Test Data

```bash
# Start log producer (generates fake application logs)
cd producers/log-producer
python producer.py
```

### 4. Process Logs

```bash
# Start event processor (consumes logs, creates embeddings, stores in Qdrant)
cd services/event-processor
python processor.py
```

### 5. Start API Gateway

```bash
# Start FastAPI server
cd services/api-gateway
python -m app.main
```

### 6. Use CLI

```bash
# Install CLI dependencies
cd frontend/cli
pip install -r requirements.txt

# Ask questions about your logs
python openops.py query "What database errors are happening?"
python openops.py search "timeout" --limit 5
python openops.py health
```

## Current Status

**✅ IMPLEMENTED:**
- Core event pipeline (Kafka → Event Processor → Qdrant)
- Log producer with realistic fake data
- Event processor with embedding generation
- LLM service with RAG (Retrieval-Augmented Generation)
- FastAPI gateway with query/search endpoints
- CLI tool for querying logs
- End-to-end integration tests

**🚧 IN PROGRESS:**
- TimescaleDB integration for metrics
- Anomaly detection
- Web UI

## Project Structure

```
openops/
├── infra/
│   ├── docker-compose.yml     # Full infrastructure stack
│   └── redpanda/              # Redpanda configuration
├── services/
│   ├── api-gateway/           # FastAPI REST API
│   ├── event-processor/       # Kafka consumer → Qdrant
│   └── llm-service/           # Ollama + RAG service
├── producers/
│   └── log-producer/          # Fake log generator
├── frontend/
│   └── cli/                   # Command-line interface
├── tests/
│   └── test_integration_e2e.py # End-to-end tests
├── docs/                      # Documentation and articles
├── ARCHITECTURE.md            # System design
└── ROADMAP.md                 # Development phases
```

## Development

### Prerequisites
- Docker Desktop
- Python 3.11+
- 4GB+ RAM for Docker

### Running Tests

```bash
# Run full end-to-end test
cd tests
python test_integration_e2e.py
```

### API Endpoints

- `GET /health` - System health check
- `POST /query/` - Ask questions using LLM + RAG
- `POST /search/` - Direct semantic search in logs
- `GET /docs` - Interactive API documentation

## Example Queries

```bash
# Natural language queries
openops query "What authentication errors happened today?"
openops query "Show me slow database queries" --time 1h
openops query "Any payment service issues?" --service payment-service

# Direct search
openops search "database timeout" --limit 10
openops search "500 error" --level ERROR
```

## License

TBD (Apache 2.0 or MIT)

## Contributing

This project is in active development. See [ROADMAP.md](ROADMAP.md) for current status and upcoming features.

---