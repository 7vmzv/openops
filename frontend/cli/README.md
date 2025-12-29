# OpenOps CLI

Simple command-line interface for OpenOps AI DevOps assistant.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Mode

```bash
# Check system health
python openops.py health

# Ask questions about logs
python openops.py query "What database errors happened?"
python openops.py query "Show me payment issues" --service payment-service --time 1h

# Search logs directly
python openops.py search "timeout" --limit 10
python openops.py search "authentication failed" --level ERROR

# List available services
python openops.py services
```

### Interactive Mode

```bash
# Start chat-like interface
python chat.py
```

Then type naturally:
```
🤖 OpenOps> What database errors happened?
🤖 OpenOps> health
🤖 OpenOps> search timeout
🤖 OpenOps> services
🤖 OpenOps> quit
```

## Examples

### Health Check
```bash
$ python openops.py health

🔍 Checking OpenOps system health...
✅ System Status: HEALTHY
📅 Timestamp: 2025-01-27T10:30:00
🔢 Version: 1.0.0

📊 Services:
  ✅ qdrant: healthy
  ✅ ollama: healthy
```

### Query Logs
```bash
$ python openops.py query "What payment errors occurred?"

🤖 Asking OpenOps: What payment errors occurred?

💡 Answer (error_analysis query):
   The logs show several payment processing failures, primarily from the payment-service.
   Main issues include database timeouts and failed API calls to external payment providers.

📊 Found 3 relevant logs (1250ms)

📋 Context logs:
  1. [ERROR] payment-service: Failed to process payment for order abc123... (0.89)
  2. [ERROR] payment-service: Database connection timeout after 5000ms... (0.85)
  3. [WARNING] api-gateway: Payment API request failed: /pay - status 500... (0.78)
```

### Search Logs
```bash
$ python openops.py search "database timeout" --limit 5

🔍 Searching logs for: database timeout

📊 Found 5 matching logs (340ms)

📋 Results:
  1. [ERROR] payment-service | 2025-01-27 10:25:30
     Database connection timeout after 5000ms (0.92)

  2. [ERROR] user-service | 2025-01-27 10:23:15
     Database query timeout: SELECT * FROM users WHERE... (0.88)
```

## Configuration

Set environment variables or use `--api` flag:

```bash
# Use different API endpoint
python openops.py --api http://production-api:8000 health

# Or set environment variable
export OPENOPS_API=http://production-api:8000
python openops.py health
```

## Commands Reference

| Command | Description | Example |
|---------|-------------|---------|
| `health` | Check system health | `python openops.py health` |
| `query` | Ask LLM questions | `python openops.py query "What happened?"` |
| `search` | Direct log search | `python openops.py search "error"` |
| `services` | List services | `python openops.py services` |

### Query Options
- `--limit N` - Max logs to analyze (default: 5)
- `--time FILTER` - Time filter: 1h, 24h, 7d
- `--service NAME` - Filter by service name
- `--level LEVEL` - Filter by log level (INFO, WARNING, ERROR, CRITICAL)

### Search Options
- `--limit N` - Max results (default: 10)
- `--time FILTER` - Time filter: 1h, 24h, 7d
- `--service NAME` - Filter by service name
- `--level LEVEL` - Filter by log level