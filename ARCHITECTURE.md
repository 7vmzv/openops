# OpenOps Copilot - Architecture

## 🎯 Project Goal

Build an AI DevOps assistant that observes systems via events, stores knowledge, detects anomalies, and answers questions like:
- "What caused the spike in errors today?"
- "What was deployed in the last hour?"
- "Show me anomalies in service X."
- "Why is latency increasing on the API gateway?"

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         FRONTEND                            │
│  • CLI (Phase 1) → Web UI (Phase 2)                        │
│  • Chat interface + event timeline                          │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP/WebSocket
                             │
┌────────────────────────────▼────────────────────────────────┐
│                      API GATEWAY                            │
│  • FastAPI                                                  │
│  • Endpoints: /query, /search, /anomalies, /events         │
│  • Auth (optional for MVP)                                  │
└─────┬──────────────────────────────────────────────────┬───┘
      │                                                   │
      │ /query                                    /search, /events
      │                                                   │
┌─────▼──────────────────────┐              ┌────────────▼──────┐
│     LLM SERVICE            │              │   QUERY SERVICE   │
│  • Ollama (local LLM)      │              │  • Direct queries │
│  • RAG: retrieve context   │◄─────────────┤  • Filters        │
│    from vector store       │   context    │  • Aggregations   │
│  • Tool calling (optional) │              └───────────────────┘
└─────┬──────────────────────┘
      │ semantic search
      │
┌─────▼──────────────────────────────────────────────────────┐
│                    VECTOR STORE (Qdrant)                   │
│  • Stores: log embeddings, event embeddings                │
│  • Metadata: timestamp, service, severity, tags            │
│  • Enables: semantic search, similarity, clustering        │
└────────────────────────────▲───────────────────────────────┘
                             │ write embeddings
                             │
┌────────────────────────────┴───────────────────────────────┐
│                   EVENT PROCESSOR                          │
│  • Kafka consumer (logs, metrics, deployments, alerts)     │
│  • Parse → Normalize → Enrich                              │
│  • Generate embeddings (sentence-transformers)             │
│  • Compute features (error_rate, latency_p95, etc.)        │
│  • Detect anomalies (z-score, thresholds)                  │
│  • Write to: Qdrant + TimescaleDB + Kafka (insights)       │
└────────────────────────────▲───────────────────────────────┘
                             │ consume
                             │
┌────────────────────────────┴───────────────────────────────┐
│                    KAFKA / REDPANDA                         │
│  Topics:                                                    │
│    • logs.raw          (application logs)                   │
│    • metrics.raw       (Prometheus, StatsD, etc.)           │
│    • deployments       (CI/CD events)                       │
│    • alerts.raw        (PagerDuty, Alertmanager)            │
│    • insights          (anomalies, summaries)               │
└────────────────────────────▲───────────────────────────────┘
                             │ produce
                             │
┌────────────────────────────┴───────────────────────────────┐
│                    EVENT PRODUCERS                          │
│  • Log shippers (Fluentd, Vector, Filebeat)                │
│  • Metrics exporters (Prometheus remote write)              │
│  • CI/CD webhooks (GitHub Actions, GitLab, Jenkins)        │
│  • Alert webhooks (PagerDuty, Opsgenie)                    │
└─────────────────────────────────────────────────────────────┘

                    ┌──────────────────────┐
                    │   TIMESCALEDB        │
                    │  • Time-series data  │
                    │  • Features/metrics  │
                    │  • Anomaly scores    │
                    │  • Deployment history│
                    └──────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology | Why |
|-----------|-----------|-----|
| **Message Bus** | Redpanda | Kafka-compatible, lighter |
| **Vector Store** | Qdrant | Fast, metadata filtering |
| **Time-Series DB** | TimescaleDB | PostgreSQL + time-series |
| **LLM** | Ollama (llama3) | Local, private, swappable |
| **Embeddings** | sentence-transformers | Fast, good quality |
| **API** | FastAPI | Modern, async, WebSocket |
| **Event Processor** | Python (asyncio) | Simple, flexible |
| **Frontend** | CLI → Streamlit/React | Incremental |
| **Orchestration** | Docker Compose → K8s | Start simple, scale later |

---

## 📊 Data Flows

### Ingestion Flow
```
App logs → Fluentd → Kafka (logs.raw)
                ↓
        Event Processor
                ↓
    ┌───────────┴───────────┐
    ↓                       ↓
Qdrant (embeddings)   TimescaleDB (metrics)
```

### Query Flow
```
User: "Why did errors spike at 14:00?"
        ↓
    API Gateway
        ↓
    LLM Service
        ↓
    1. Semantic search in Qdrant (retrieve relevant logs)
    2. Query TimescaleDB (get error_rate_5m around 14:00)
    3. Prompt LLM with context
        ↓
    "At 14:00, error rate jumped from 2/min to 45/min.
     Logs show 'Database connection timeout' from service-X.
     Deployment of v1.2.3 happened at 13:58."
```

---

## 🧩 Key Architectural Decisions

### 1. TimescaleDB over Feast
- Feast is overkill for MVP
- TimescaleDB = PostgreSQL + time-series optimizations
- Simpler to query, backup, and operate
- Supports feature engineering via materialized views

### 2. Single Event Processor
- One service handles: consume → parse → embed → detect → store
- Easier to debug and iterate
- Can split later when scaling

### 3. Redpanda over Kafka
- No JVM (lighter, faster startup)
- Kafka-compatible API
- Single binary, easier Docker setup

### 4. Ollama for LLM
- No API costs
- Privacy-friendly (local)
- Easy to swap models
- Can add OpenAI/Anthropic later

### 5. Qdrant for Vector Store
- Fast, Rust-based
- Great filtering (metadata + vector search)
- Easy Docker deployment

---

## 💡 Use Cases

1. **Log understanding**: "Explain these logs", "Group similar error patterns"
2. **Anomaly detection**: "Why did CPU jump at 13:00?"
3. **Deployment intelligence**: "What changed since last deployment?"
4. **CI/CD analysis**: "Why did pipeline #242 fail?"
5. **SLO/SLA reasoning**: "Which services are at risk of violating SLO?"
6. **Root-cause analysis**: "Find root cause candidates for this outage"

---

## 📁 Project Structure

```
openops/
├── services/
│   ├── event-processor/       # Kafka consumer → embeddings → storage
│   ├── llm-service/            # Ollama + RAG
│   ├── api-gateway/            # FastAPI
│   └── query-service/          # Direct DB queries
├── producers/
│   ├── log-producer/           # Simulate logs (testing)
│   └── metric-producer/        # Simulate metrics
├── infra/
│   ├── docker-compose.yml      # Full stack
│   ├── redpanda/               # Config
│   ├── qdrant/                 # Config
│   └── timescaledb/            # Init scripts
├── shared/
│   ├── schemas/                # Event schemas
│   └── utils/                  # Common code
├── frontend/
│   ├── cli/                    # CLI tool
│   └── web/                    # Web UI (later)
├── tests/
├── docs/
├── .github/workflows/          # CI/CD
├── README.md
└── LICENSE
```
