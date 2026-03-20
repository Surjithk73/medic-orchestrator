# Medic Orchestrator 🧬

> Autonomous drug repurposing intelligence platform powered by multi-agent LLMs

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Overview

Medic Orchestrator is an AI-powered research platform that analyzes drug repurposing opportunities by orchestrating multiple specialized agents across clinical, patent, market, and regulatory domains. Simply input a molecule name and receive a comprehensive repurposing report in minutes.

### Key Features

- 🤖 **Multi-Agent Architecture** — 4 specialized agents (Clinical, Patent, Market, Regulatory) working in parallel
- 🔄 **Real-Time Progress** — Server-Sent Events (SSE) for live pipeline updates
- ⚡ **Smart Caching** — 7-day Redis cache for instant responses on popular molecules
- 📊 **RAG Pipeline** — Semantic chunking + Gemini embeddings + Qdrant vector search
- 🎯 **LLM Routing** — 3-tier fallback (Gemini 2.5 Flash → Pro → NVIDIA Nemotron)
- 📚 **Citation Tracking** — Every claim linked to its source
- 🔍 **Conflict Detection** — Automatic cross-domain contradiction flagging

## Architecture

```
User Input (Molecule Name)
    ↓
ChEMBL Resolution → Canonical Name
    ↓
┌─────────────────────────────────┐
│   LangGraph Orchestration       │
├─────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐      │
│  │Clinical │  │ Patent  │      │
│  │ Agent   │  │ Agent   │      │
│  └─────────┘  └─────────┘      │
│  ┌─────────┐  ┌─────────┐      │
│  │ Market  │  │Regulatory│     │
│  │ Agent   │  │ Agent   │      │
│  └─────────┘  └─────────┘      │
└─────────────────────────────────┘
    ↓
Cross-Domain Synthesis
    ↓
Repurposing Report + Opportunities
```

## Tech Stack

**Backend:**
- FastAPI + LangGraph
- Gemini 2.5 (Flash/Pro) + NVIDIA Nemotron
- Qdrant (vector DB) + Supabase (PostgreSQL) + Upstash Redis

**Frontend:**
- Next.js 14 (App Router)
- TailwindCSS + Framer Motion
- Server-Sent Events (SSE)

**Data Sources:**
- ClinicalTrials.gov v2 API
- EPO OPS (European Patent Office)
- Open Targets GraphQL
- FDA DailyMed + OpenFDA
- ChEMBL REST API

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- API Keys (see `.env.example`)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/medic-orchestrator.git
cd medic-orchestrator
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Install Python dependencies**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

4. **Set up databases**
```bash
# Run Supabase SQL schema
psql -h your-supabase-url -f scripts/setup_supabase.sql

# Create Qdrant collections
python scripts/setup_qdrant.py
```

5. **Start the backend**
```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

6. **Start the frontend** (in a new terminal)
```bash
cd frontend
npm install
npm run dev
```

7. **Open your browser**
```
http://localhost:3000
```

## Usage

### Web Interface

1. Enter a molecule name (e.g., "Aspirin", "Metformin")
2. Watch real-time progress as agents analyze different domains
3. Review the generated repurposing report with opportunities

### API

**Start Research:**
```bash
curl -X POST http://localhost:8000/api/research/start \
  -H "Content-Type: application/json" \
  -d '{"molecule": "Aspirin"}'
```

**Stream Progress (SSE):**
```bash
curl -N http://localhost:8000/api/research/stream/{session_id}
```

**Get Report:**
```bash
curl http://localhost:8000/api/report/{session_id}
```

**Check Cache:**
```bash
curl http://localhost:8000/api/report/cache/Aspirin
```

## Features in Detail

### Multi-Agent System

Each agent specializes in a specific domain:

- **Clinical Agent** — Analyzes clinical trials from ClinicalTrials.gov
- **Patent Agent** — Assesses freedom-to-operate via EPO OPS + Open Targets
- **Market Agent** — Evaluates market landscape using OpenFDA
- **Regulatory Agent** — Reviews regulatory status via FDA DailyMed

### RAG Pipeline

1. **Retrieval** — Fetch data from external APIs
2. **Chunking** — Semantic boundary splitting (500 tokens max)
3. **Embedding** — Gemini embedding-001 (3072-dim vectors)
4. **Storage** — Qdrant vector database
5. **Search** — Hybrid vector + keyword search

### Caching System

- **Cache Key:** Canonical molecule name (e.g., "ASPIRIN")
- **Storage:** Redis with 7-day TTL
- **Performance:** 1800x faster for cached molecules (~50ms vs 90s)
- **Invalidation:** Manual via API or automatic expiry

### SSE Streaming

Real-time events:
- `planner_started` / `planner_completed`
- `agent_started` / `agent_completed` (per domain)
- `synthesis_started` / `synthesis_complete`

## Configuration

### LLM Models

Edit `backend/models/llm_router.py`:
```python
# Primary: Gemini 2.5 Flash (fast)
# Secondary: Gemini 2.5 Pro (stronger reasoning)
# Fallback: NVIDIA Nemotron (free tier)
```

### Cache TTL

Edit `backend/memory/report_cache.py`:
```python
report_cache = ReportCache(ttl_days=7)  # Change to 14, 30, etc.
```

### API Rate Limits

- Gemini Free Tier: 20 requests/day (Flash), 0 (Pro)
- OpenRouter: Varies by model
- ClinicalTrials.gov: No auth required
- EPO OPS: 2500 requests/week (requires registration)

## Project Structure

```
medic-orchestrator/
├── backend/
│   ├── agents/          # Domain-specific agents
│   ├── api/             # FastAPI routes
│   ├── db/              # Database clients
│   ├── graph/           # LangGraph orchestration
│   ├── memory/          # Context, cache, citations
│   ├── models/          # Schemas & LLM router
│   ├── retrieval/       # RAG pipeline
│   └── synthesis/       # Cross-domain synthesis
├── frontend/
│   └── src/
│       ├── app/         # Next.js pages
│       ├── components/  # React components
│       └── hooks/       # Custom hooks (SSE)
├── scripts/             # Setup scripts
├── tests/               # Test suite
└── docs/                # Documentation
```

## Documentation

- [SSE Implementation](SSE_IMPLEMENTATION.md)
- [Caching Guide](CACHING.md)
- [API Requirements](api_requirements.md)
- [Project Overview](ProjectOverview.md)
- [Tasks & Progress](tasks.md)

## Testing

```bash
# Run all tests
pytest tests/

# Run specific phase
pytest tests/test_phase6_agents.py

# Run with coverage
pytest --cov=backend tests/
```

## Deployment

### Docker

```bash
docker-compose up -d
```

### Manual

1. Deploy backend to any Python hosting (Railway, Render, Fly.io)
2. Deploy frontend to Vercel
3. Set environment variables in hosting platform
4. Update CORS origins in `backend/main.py`

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details

## Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) for orchestration
- [Gemini API](https://ai.google.dev/) for LLM capabilities
- [ClinicalTrials.gov](https://clinicaltrials.gov/) for clinical data
- [ChEMBL](https://www.ebi.ac.uk/chembl/) for molecule resolution
- [Qdrant](https://qdrant.tech/) for vector search

## Contact

For questions or support, please open an issue on GitHub.

---

**⚠️ Disclaimer:** This tool is for research purposes only. Always consult qualified professionals for medical and regulatory decisions.
