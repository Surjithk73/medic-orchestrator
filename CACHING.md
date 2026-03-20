# Report Caching Implementation

## Overview

The system now caches completed research reports in Redis to avoid re-running expensive pipelines for the same molecule. This significantly improves response time and reduces API costs for frequently requested compounds.

## How It Works

### Cache Flow

```
User requests "Aspirin"
    ↓
Resolve canonical name via ChEMBL → "ASPIRIN"
    ↓
Check Redis cache for "ASPIRIN"
    ↓
┌─────────────────┬─────────────────┐
│   Cache HIT     │   Cache MISS    │
├─────────────────┼─────────────────┤
│ Return cached   │ Run full        │
│ report (instant)│ pipeline        │
│                 │ Cache result    │
└─────────────────┴─────────────────┘
```

### Cache Key Strategy

- **Key format**: `report_cache:{CANONICAL_NAME}`
- **Example**: `report_cache:ASPIRIN`, `report_cache:METFORMIN`
- **Normalization**: All names converted to uppercase for consistency
- **TTL**: 7 days (configurable)

### What Gets Cached

The complete `FinalReportSchema`:
- `executive_summary`
- `mechanism_of_action`
- `opportunities` (list of repurposing opportunities)
- `data_gaps`

## API Changes

### POST /api/research/start

**New request field:**
```json
{
  "molecule": "Aspirin",
  "force_refresh": false  // Optional: bypass cache
}
```

**New response fields:**
```json
{
  "session_id": "uuid",
  "status": "complete",  // "complete" if from cache, "running" if new
  "canonical": "ASPIRIN",
  "estimated_duration_seconds": 0,  // 0 if cached, 180 if new
  "from_cache": true  // Indicates cache hit
}
```

### GET /api/report/cache/{molecule}

Check if a molecule is cached:

```bash
curl http://localhost:8000/api/report/cache/Aspirin
```

Response:
```json
{
  "molecule": "Aspirin",
  "cached": true,
  "ttl_seconds": 604800,
  "ttl_hours": 168.0
}
```

### DELETE /api/report/cache/{molecule}

Manually invalidate a cached report:

```bash
curl -X DELETE http://localhost:8000/api/report/cache/Aspirin
```

Response:
```json
{
  "molecule": "Aspirin",
  "status": "invalidated"
}
```

## Benefits

### Performance
- **Cache hit**: ~50ms (instant)
- **Cache miss**: ~90-180 seconds (full pipeline)
- **Improvement**: 1800x faster for cached molecules

### Cost Savings
- Avoids redundant LLM API calls (5 calls per pipeline)
- Reduces ClinicalTrials.gov, EPO, FDA API usage
- Saves Qdrant vector storage operations

### User Experience
- Popular molecules (Aspirin, Metformin, etc.) return instantly
- No waiting for frequently requested compounds
- Consistent results for same molecule

## Cache Management

### Automatic Expiration
- Reports auto-expire after 7 days
- Ensures data freshness (clinical trials, patents update)
- Configurable via `ReportCache(ttl_days=7)`

### Manual Invalidation
Use when:
- New clinical trial data available
- Patent status changes
- Regulatory updates occur

```python
from backend.memory.report_cache import report_cache
await report_cache.invalidate("ASPIRIN")
```

### Force Refresh
Users can bypass cache:
```json
POST /api/research/start
{
  "molecule": "Aspirin",
  "force_refresh": true
}
```

## Implementation Details

### Storage
- **Backend**: Upstash Redis (already in use)
- **Serialization**: JSON
- **Compression**: None (Redis handles this)

### Cache Key Normalization
```python
"Aspirin" → "ASPIRIN"
"metformin" → "METFORMIN"
"Sildenafil Citrate" → "SILDENAFIL CITRATE"
```

### TTL Management
```python
# Set with TTL
await report_cache.set("ASPIRIN", report_data)

# Check remaining TTL
ttl = await report_cache.get_ttl("ASPIRIN")  # Returns seconds

# Exists check
exists = await report_cache.exists("ASPIRIN")  # Returns bool
```

## Monitoring

### Cache Hit Rate
Track via logs:
```
[session_id] Serving cached report for ASPIRIN (TTL: 604800s)
```

### Cache Misses
Track via logs:
```
Cached report for ASPIRIN (TTL: 604800s)
```

## Configuration

### Change TTL
```python
# In backend/memory/report_cache.py
report_cache = ReportCache(ttl_days=14)  # 14 days instead of 7
```

### Disable Caching
```python
# In backend/api/research_router.py
# Comment out cache check:
# cached_report = await report_cache.get(canonical_name)
```

## Testing

### Test Cache Hit
```bash
# First request (cache miss)
curl -X POST http://localhost:8000/api/research/start \
  -H "Content-Type: application/json" \
  -d '{"molecule": "Aspirin"}'
# Wait for completion...

# Second request (cache hit)
curl -X POST http://localhost:8000/api/research/start \
  -H "Content-Type: application/json" \
  -d '{"molecule": "Aspirin"}'
# Returns instantly with from_cache: true
```

### Test Force Refresh
```bash
curl -X POST http://localhost:8000/api/research/start \
  -H "Content-Type: application/json" \
  -d '{"molecule": "Aspirin", "force_refresh": true}'
# Bypasses cache, runs full pipeline
```

### Check Cache Status
```bash
curl http://localhost:8000/api/report/cache/Aspirin
```

## Future Enhancements

1. **Cache warming** — pre-cache top 100 molecules
2. **Partial caching** — cache agent summaries separately
3. **Cache analytics** — track hit rate, popular molecules
4. **Smart invalidation** — auto-invalidate on data source updates
5. **Distributed cache** — Redis Cluster for scale
