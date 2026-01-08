# OpenOps Copilot

AI-powered DevOps assistant that analyzes logs and answers questions about your infrastructure.

## Quick Start

```bash
# 1. Start services
cd infra
docker-compose up -d

# 2. Generate test data
cd ../producers/log-producer
python producer.py  # Run for 30 seconds, then Ctrl+C

# 3. Process logs
cd ../../services/event-processor
python processor.py  # Run for 20 seconds, then Ctrl+C

# 4. Start API
cd ../api-gateway
python -m app.main

# 5. Use CLI
cd ../../frontend/cli
python openops.py query "What database errors are happening?"
```

## What It Does

- **Ingests logs** from your applications
- **Understands context** using AI embeddings
- **Answers questions** like "What caused the errors?" or "Show me slow queries"
- **Provides insights** about system health and issues

## Architecture

```
Logs → Kafka → AI Processing → Vector DB → LLM → Answers
```

## Services

- **Redpanda Console**: http://localhost:8080
- **Qdrant Dashboard**: http://localhost:6333/dashboard  
- **API Documentation**: http://localhost:8000/docs
- **Ollama API**: http://localhost:11434

## CLI Commands

```bash
# Check system health
openops health

# Ask questions
openops query "What errors happened?"
openops query "Show me payment issues" --service payment-service

# Search logs directly
openops search "timeout" --limit 5

# Interactive mode
python chat.py
```

## Status

✅ **Working**: Log processing, AI analysis, API, CLI  
🚧 **Next**: Metrics, anomaly detection, web UI

## Requirements

- Docker Desktop
- Python 3.11+
- 4GB+ RAM