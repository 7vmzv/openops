# OpenOps Usage Examples

## CLI Commands

### Health Check
```bash
openops health
```

### Ask Questions
```bash
# General questions
openops query "What errors happened?"
openops query "Show me system status"
openops query "Any performance issues?"

# Specific service
openops query "What's wrong with payments?" --service payment-service

# Time-filtered
openops query "Database errors in last hour" --time 1h

# Level-filtered
openops query "Show critical issues" --level CRITICAL
```

### Direct Search
```bash
# Search for specific terms
openops search "timeout"
openops search "database connection"
openops search "authentication failed"

# With filters
openops search "error" --service api-gateway --limit 10
openops search "slow" --time 24h --level WARNING
```

### Interactive Mode
```bash
python chat.py
```

Then type questions naturally:
- "What database errors happened?"
- "Show me payment service issues"
- "Any authentication failures?"

## API Examples

### Query Endpoint
```bash
curl -X POST "http://localhost:8000/query/" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What database errors are happening?",
    "limit": 5
  }'
```

### Search Endpoint
```bash
curl -X POST "http://localhost:8000/search/" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "timeout",
    "limit": 10,
    "service_filter": "payment-service"
  }'
```

### Health Check
```bash
curl "http://localhost:8000/health/"
```

## Common Use Cases

### Incident Response
```bash
# What's happening right now?
openops query "What errors are happening?" --time 1h

# Focus on specific service
openops query "Payment service issues" --service payment-service

# Check critical problems
openops query "Show critical issues" --level CRITICAL
```

### System Monitoring
```bash
# Overall health
openops query "System status summary"

# Performance check
openops query "Any slow queries or timeouts?"

# Authentication issues
openops query "Authentication or login problems"
```

### Troubleshooting
```bash
# Database problems
openops search "database" --level ERROR

# Network issues
openops search "timeout OR connection" --time 24h

# Service-specific
openops query "Why is the API gateway slow?" --service api-gateway
```

## Response Format

All queries return structured responses with:
- **Answer**: AI-generated explanation
- **Query Type**: Detected category (error_analysis, performance, etc.)
- **Logs Found**: Number of relevant logs
- **Context Logs**: The actual logs that informed the answer
- **Processing Time**: How long the query took

## Tips

- Use natural language - the AI understands context
- Be specific about time ranges for recent issues
- Filter by service when investigating specific components
- Use search for exact terms, query for explanations
- Interactive mode is great for exploratory analysis