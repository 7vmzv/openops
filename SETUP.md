# OpenOps Setup Guide

## Prerequisites

- Docker Desktop running
- Python 3.11+
- 4GB+ RAM

## 1. Start Services

```bash
cd infra
docker-compose up -d
```

Wait 30 seconds for services to start.

## 2. Verify Services

```bash
docker-compose ps
```

All services should show "healthy" or "running".

## 3. Pull AI Model

```bash
python test_ollama.py
```

This downloads the llama3.2:1b model (~1GB).

## 4. Generate Test Data

```bash
cd ../producers/log-producer
pip install -r requirements.txt
python producer.py
```

Run for 30 seconds, then press Ctrl+C.

## 5. Process Logs

```bash
cd ../../services/event-processor
pip install -r requirements.txt
python processor.py
```

Run for 20 seconds, then press Ctrl+C.

## 6. Start API

```bash
cd ../api-gateway
pip install -r requirements.txt
python -m app.main
```

API will start on http://localhost:8000

## 7. Use CLI

Open new terminal:

```bash
cd frontend/cli
pip install -r requirements.txt
python openops.py health
python openops.py query "What database errors are happening?"
```

## Troubleshooting

**Services not starting?**
- Check Docker Desktop is running
- Try `docker-compose down && docker-compose up -d`

**Ollama timeout?**
- Model is downloading, wait a few minutes
- Check with `docker logs openops-ollama`

**No logs found?**
- Make sure you ran the producer and processor steps
- Check Qdrant at http://localhost:6333/dashboard

## Quick Test

```bash
cd tests
pip install -r requirements.txt
python test_integration_e2e.py
```

This runs a full end-to-end test.