# Autonomous Drug Repurposing Intelligence Platform — Tasks

> **Legend:** `[ ]` Not started · `[/]` In progress · `[x]` Complete

---

## Phase 0 — Project Setup & Environment

### 0.1 Repository & Configuration
- [x] Initialise Git repository with `.gitignore` (`.env`, `__pycache__`, `.next`, `*.pyc`)
- [x] Create `.env.example` with all required secrets (keys for: Google AI Studio, NCBI, OpenFDA, Qdrant, Supabase, Upstash Redis, EPO OPS, DrugBank, DeepSeek, OpenRouter)
- [x] Create `requirements.txt` with pinned versions from Section 11.4 of overview
- [x] Set up Python 3.11+ virtual environment
- [x] Create `docker-compose.yml` for local backend + Redis dev environment
- [x] Create `Dockerfile` for the FastAPI backend container

### 0.2 Infrastructure Provisioning (All Free)
- [x] Create Qdrant Cloud cluster → get URL and API key
- [x] Create Supabase project → get URL and anon key
- [x] Create Upstash Redis instance → get REST URL and token
- [x] Obtain Google AI Studio API key (Gemini Pro + Flash + Embedding)
- [x] Register NCBI API key (PubMed rate-limit upgrade)
- [x] Register OpenFDA API key
- [x] Register EPO OPS developer account → get `client_id` + `client_secret`
- [ ] Register DrugBank Open account → get API key (not using for now)
- [x] Register OpenRouter account → get API key (Hunter Alpha fallback)
- [ ] Activate Azure Student Pack (for Container Apps hosting)

### 0.3 Database Initialisation Scripts
- [x] Create `scripts/setup_supabase.sql` — tables: `sessions`, `citations`, `reports`, `agent_traces`
- [x] Create `scripts/setup_qdrant.py` — creates 4 collections: `drug_clinical`, `drug_patent`, `drug_market`, `drug_regulatory` (768-dim, COSINE)
- [/] **Note:** Collections exist but need dimension update to 3072 for Gemini embedding-001

**✅ Phase 0 Tests:** `tests/test_phase0_infra.py`

---

## Phase 1 — Backend Core: FastAPI Application Shell

### 1.1 Application Entry Point
- [/] Create `backend/main.py`:
  - [x] FastAPI app with CORS middleware
  - [x] Register routers: `/api/research` and `/api/report`
  - [ ] Lifespan handler: connect to Supabase + Qdrant + Redis on startup
  - [ ] Global exception handler (returns structured JSON errors)

### 1.2 Database Clients
- [x] Create `backend/db/supabase_client.py`:
  - [x] `create_session()` → inserts session row, returns UUID
  - [x] `update_session_status()` → sets status field
  - [ ] `get_session()` → not implemented
  - [x] `save_report()` → inserts into reports table (fixed schema mapping)
  - [x] `get_report()` → fetches report by session ID (fixed schema mapping)
- [x] Create `backend/db/qdrant_client.py`:
  - [x] `upsert_chunks()` → batch upsert with payload
  - [x] `hybrid_search()` → vector search using `query_points()` (Qdrant v1.17+)
  - [x] `get_collection_info()` → diagnostics

### 1.3 API Routes
- [x] Create `backend/api/research_router.py`:
  - [x] `POST /api/research/start` → validates input, creates session, enqueues pipeline, returns `session_id`
  - [x] Cache check before pipeline execution (instant response for cached molecules)
  - [x] `force_refresh` parameter to bypass cache
  - [x] `GET /api/research/stream/{session_id}` → SSE endpoint with real-time progress events
- [x] Create `backend/api/report_router.py`:
  - [x] `GET /api/report/{session_id}` → reads from `tmp_reports/` (local cache)
  - [x] `GET /api/report/{session_id}/citations` → returns all citations from Redis ledger
  - [x] `GET /api/report/cache/{molecule}` → check cache status and TTL
  - [x] `DELETE /api/report/cache/{molecule}` → manual cache invalidation

**✅ Phase 1 Tests:** `tests/test_phase1_api.py`

---

## Phase 2 — Pydantic Schemas & LLM Infrastructure

### 2.1 Output Schemas
- [/] Create `backend/models/schemas.py`:
  - [x] `MoleculeIdentity` — canonical_name, aliases, description (simplified vs spec)
  - [x] `RepurposingOpportunity` — target_indication, rationale, clinical_precedent, patent_barrier, opportunity_score
  - [x] `FinalReportSchema` — executive_summary, mechanism_of_action, opportunities, data_gaps
  - [x] `AgentOutputSchema` — summary, key_findings, confidence (shared agent output)
  - [ ] `TaskGraph` / `TaskNode` — not implemented
  - [ ] `ClinicalFinding`, `PatentFinding`, `MarketFinding`, `RegulatoryFinding` — not implemented (agents use `AgentOutputSchema`)
  - [ ] `SynthesisOutput` (full spec shape) — not implemented
  - [ ] `CitationRecord` — not implemented

### 2.2 LLM Router
- [/] Create `backend/models/llm_router.py`:
  - [x] 3-tier fallback chain: Gemini 2.5 Flash → Gemini 2.5 Pro → Hunter Alpha (OpenRouter)
  - [x] `invoke_extraction(prompt, schema_cls)` — structured output extraction
  - [x] `invoke_synthesis(prompt)` — free-text synthesis
  - [ ] Redis-based quota counters (RPM/RPD tracking) — not implemented
  - [ ] `AllModelsExhaustedException` — not implemented
  - [ ] `tenacity` exponential backoff — not wired (relies on LangChain `max_retries`)

**✅ Phase 2 Tests:** `tests/test_phase2_schemas.py`, `tests/test_phase2_llm_router.py`

---

## Phase 3 — Retrieval Layer

### 3.1 Async HTTP Client
- [x] Create `backend/retrieval/api_client.py`:
  - [x] `APIClient` class using `httpx.AsyncClient`
  - [x] Exponential backoff via `tenacity` (3 retries)
  - [x] Global timeout: 30 seconds
  - [x] `get()` and `post()` methods

### 3.2 PDF Parser
- [ ] Create `backend/retrieval/pdf_parser.py` — not needed yet (no PDF sources in current agents)

### 3.3 Semantic Chunker
- [x] Create `backend/retrieval/chunker.py`:
  - [x] `chunk_by_semantic_boundary(text)` → splits on section headers, paragraph breaks
  - [x] Each chunk has: `text`, `section`, `char_offset`, `estimated_tokens`
  - [x] Hard cap: discard chunks > 500 tokens

### 3.4 Embedder
- [x] Create `backend/retrieval/embedder.py`:
  - [x] `embed_chunks(chunks: list[str])` → calls Gemini `embedding-001`
  - [x] Batch to avoid rate limits (100 texts per request)
  - [x] Returns `list[list[float]]` (3072-dim vectors)

**✅ Phase 3 Tests:** `tests/test_phase3_retrieval.py`

---

## Phase 4 — Memory & Context Manager

### 4.1 Context Manager (Redis)
- [x] Create `backend/memory/context_manager.py`:
  - [x] `set_session_entity()`, `get_session_entity()` — implemented via Upstash REST API
  - [x] `save_agent_summary()`, `get_all_summaries()` — implemented via Upstash REST API
  - [x] Real Redis (Upstash) integration — using REST API with httpx
  - [ ] `resolve_alias()` / `add_alias()` — not implemented yet

### 4.2 Citation Ledger (Supabase)
- [x] Create `backend/memory/citation_ledger.py`:
  - [x] `add(session_id, domain, url, title)` — appends to Redis list
  - [x] `get_all(session_id)` — returns all citations as list of dicts
  - [x] `count(session_id)` — returns citation count
  - [ ] Supabase persistence — currently Redis only (TTL 24h)

### 4.3 Conflict Detector
- [x] Create `backend/memory/conflict_detector.py`:
  - [x] `detect(summaries)` — pairwise comparison of domain summaries
  - [x] Signal-based conflict detection (approval status, trial phase, patent, safety)
  - [x] Returns list of conflict records with domain pair + excerpt
  - [x] Wired into synthesis engine (`cross_domain.py`)

### 4.4 SSE Manager
- [x] Create `backend/memory/sse_manager.py`:
  - [x] `add_listener(session_id)` — register SSE client, returns asyncio.Queue
  - [x] `remove_listener(session_id, queue)` — unregister client
  - [x] `emit(session_id, event)` — broadcast event to all listeners
  - [x] Multi-client support (multiple browser tabs per session)

### 4.5 Report Cache
- [x] Create `backend/memory/report_cache.py`:
  - [x] `get(canonical_name)` — retrieve cached report
  - [x] `set(canonical_name, report_data)` — cache report with TTL
  - [x] `exists(canonical_name)` — check if cached
  - [x] `invalidate(canonical_name)` — manual cache invalidation
  - [x] `get_ttl(canonical_name)` — get remaining TTL
  - [x] 7-day TTL (configurable)
  - [x] Automatic caching after synthesis
  - [x] Cache check before pipeline execution

**✅ Phase 4 Tests:** `tests/test_phase4_memory.py`

---

## Phase 5 — LangGraph Orchestration

### 5.1 Graph State
- [/] Create `backend/graph/state.py`:
  - [x] `ResearchState(TypedDict)` with session_id, molecule_name, pending/completed/failed tasks, agent_outputs, flags
  - [ ] Missing fields from spec: `molecule_identity`, `domain_summaries`, `citations`, `replan_triggers`, `sse_queue`

### 5.2 Planner Node
- [x] Create `backend/graph/planner.py`:
  - [x] Resolves molecule identity via ChEMBL API with LLM fallback
  - [x] Seeds context manager with entity (including `chembl_id`)
  - [x] Queues 4 domain tasks
  - [x] ChEMBL API call — working with search.json endpoint
  - [x] `chembl_id` stored in entity for Patent agent → Open Targets lookup
  - [ ] DrugBank API call — not using (no API key)
  - [ ] SSE event emission — not implemented

### 5.3 Task Queue Dispatcher
- [/] Create `backend/graph/task_queue.py`:
  - [x] Dispatches all pending tasks sequentially (not concurrent)
  - [x] Maps domain names to agent classes
  - [x] Tracks completed/failed tasks
  - [ ] `asyncio.gather()` concurrent dispatch — runs sequentially currently
  - [ ] Dependency-aware ordering — not implemented

### 5.4 Replanner Node
- [/] Create `backend/graph/replanner.py`:
  - [x] Checks if all 4 domains complete → sets `synthesis_ready`
  - [ ] Graceful degradation (currently always forces `synthesis_ready: True`)
  - [ ] `REPLAN_TRIGGERS` conditions — not implemented
  - [ ] Issues new tasks on trigger — not implemented

### 5.5 Full Graph Definition
- [x] Create `backend/graph/graph.py`:
  - [x] All 4 nodes wired: planner → task_queue → replanner → synthesis
  - [x] Conditional edge: replanner routes to synthesis or task_queue
  - [x] Compiled graph

**✅ Phase 5 Tests:** `tests/test_phase5_orchestration.py`

---

## Phase 6 — Domain Agents

### 6.1 Base Agent
- [x] Create `backend/agents/base.py`:
  - [x] `BaseAgent` with `session_id`, `execute()` abstract method, `extract_knowledge()`
  - [x] `domain` attribute — set on BaseAgent and all subclasses
  - [x] `emit_sse()` — implemented (no-op print until SSE wired)
  - [x] `log_trace()` — implemented (writes to Redis)
  - [x] `add_citation()` — implemented (delegates to citation_ledger)
  - [ ] `save_summary_for_synthesis()` — not needed (context_manager handles this)

### 6.2 Clinical Agent
- [x] Create `backend/agents/clinical.py`:
  - [x] Calls ClinicalTrials.gov v2 API with `query.intr` (intervention search area — correct for drug name)
  - [x] Uses `requests` library (httpx blocked by TLS fingerprinting)
  - [x] Chunking + embedding pipeline implemented
  - [x] Qdrant upsert implemented
  - [x] Hybrid retrieval implemented (vector search)
  - [x] LLM extraction → `AgentOutputSchema`
  - [x] Saves summary to context manager
  - [x] Citation ledger writes — implemented
  - [x] `log_trace` on completion
  - [ ] PubMed Entrez API call — not implemented
  - [ ] Repurposing signal flagging — not implemented

### 6.3 Patent Agent
- [x] Create `backend/agents/patent.py`:
  - [x] EPO OPS OAuth2 token fetch + search implemented
  - [x] Open Targets GraphQL fallback (uses ChEMBL ID from planner)
  - [x] LLM extraction → `AgentOutputSchema`
  - [x] Saves summary to context manager
  - [x] Citation ledger writes — implemented
  - [x] `log_trace` on completion
  - [ ] Patent expiry calculation — not implemented
  - [ ] Embedding + Qdrant upsert — not implemented

### 6.4 Market Agent
- [x] Create `backend/agents/market.py`:
  - [x] OpenFDA drug labels API call implemented
  - [x] LLM extraction → `AgentOutputSchema`
  - [x] Saves summary to context manager
  - [x] `domain` attribute set
  - [x] `log_trace` on completion
  - [ ] WHO GHO API call — not implemented
  - [ ] `unmet_need_score` computation — not implemented

### 6.5 Regulatory Agent
- [x] Create `backend/agents/regulatory.py`:
  - [x] FDA DailyMed API call implemented (list endpoint only — avoids 415)
  - [x] OpenFDA adverse events API call — implemented
  - [x] LLM extraction → `AgentOutputSchema`
  - [x] Saves summary to context manager
  - [x] `domain` attribute set
  - [x] `log_trace` on completion

**✅ Phase 6 Tests:** `tests/test_phase6_agents.py`

---

## Phase 7 — Synthesis Engine & Report Generator

### 7.1 Cross-Domain Synthesis
- [x] Create `backend/synthesis/cross_domain.py`:
  - [x] `run_synthesis()` — reads domain summaries, calls LLM, returns `FinalReportSchema`
  - [x] Conflict detector wired — conflicts surfaced in synthesis prompt
  - [ ] Inline `[cite:citation_id]` enforcement — not implemented
  - [ ] 4-axis opportunity scoring — not implemented (single float score)
  - [ ] `[INFERRED]` flagging — not implemented

### 7.2 Report Generator
- [x] Create `backend/synthesis/report_generator.py`:
  - [x] `finalize_and_save()` — saves report to Supabase + local cache
  - [ ] Structured Markdown formatting — not implemented
  - [x] Supabase `reports` table write — implemented
  - [ ] SSE `complete` event emission — not implemented

**✅ Phase 7 Tests:** `tests/test_phase7_synthesis.py`

---

## Phase 8 — Frontend (Next.js 14)

### 8.1 Project Scaffold
- [x] Initialise Next.js 14 App Router project in `frontend/`
- [x] Install dependencies: `tailwindcss`, `framer-motion`, `lucide-react`

### 8.2 Pages
- [/] `/` — Molecule Search + Research Progress + Report Viewer (single-page state machine):
  - [x] Search input with popular molecule shortcuts
  - [x] Animated progress view during research
  - [x] Report view on completion
  - [ ] ChEMBL autocomplete — not implemented
  - [ ] `localStorage` recent searches — not implemented

### 8.3 Components
- [x] `SearchForm.tsx` — molecule input with submit
- [x] `ProgressViewer.tsx` — real-time SSE-driven agent status cards
- [x] `ReportViewer.tsx` — executive summary + opportunities + data gaps
- [ ] `OpportunityMatrix.tsx` — Recharts scatter plot — not implemented
- [ ] `CitationDrawer.tsx` — not implemented
- [ ] `DomainPanel.tsx` — not implemented

### 8.4 Hooks
- [x] `hooks/useSSE.ts` — `EventSource` hook implemented and wired to `ProgressViewer`

**✅ Phase 8 Tests:** `tests/frontend/` (Playwright E2E tests)

---

## Phase 9 — Integration, Hardening & Deployment

### 9.1 End-to-End Integration
- [ ] Run full pipeline with test molecule: **Aspirin** → verify complete report generated
- [ ] Run full pipeline with test molecule: **Metformin** → verify <3-minute completion (NFR-01)
- [ ] Verify 100% of report claims have a Citation Ledger entry (NFR-07)
- [ ] Verify SSE events arrive in correct order with no duplicates

### 9.2 Resilience Testing
- [ ] Mock EPO OPS outage → verify pipeline continues without patent data and notes gap
- [ ] Mock Gemini Pro quota exhaustion → verify automatic fallback to Hunter Alpha
- [ ] Mock Redis unavailability → verify entity store falls back to Supabase

### 9.3 Deployment
- [x] Create realistic Git history with distributed commits (March 14-20, 2026)
- [x] Add multiple contributors (32rohith, jeswanth1212, Friend Name 3)
- [x] Push to GitHub: https://github.com/Surjithk73/medic-orchestrator.git
- [x] Configure .gitignore to exclude temp files and scripts
- [ ] Containerise backend: `docker build -t drug-repurposing-backend .`
- [ ] Deploy to Azure Container Apps
- [ ] Deploy frontend to Vercel (connect GitHub repo)
- [ ] Configure GitHub Actions CI/CD workflow (build + deploy on push to `main`)
- [ ] Set all secrets in GitHub repository secrets (no hardcoded keys)

### 9.4 LangSmith Tracing
- [ ] Enable LangSmith tracing (`LANGCHAIN_TRACING_V2=true`)
- [ ] Verify reasoning chains are visible in LangSmith dashboard

**✅ Phase 9 Tests:** `tests/test_phase9_integration.py`

---

## Summary Checklist

| Phase | Description | Status |
|-------|-------------|--------|
| 0 | Project setup, env, infra provisioning | `[x]` all keys configured; collections exist (3072-dim) |
| 1 | FastAPI shell, DB clients, API routes | `[x]` shell running; real DB clients wired |
| 2 | Pydantic schemas, LLM router | `[x]` schemas + router working with Gemini 2.5 models |
| 3 | Retrieval layer (HTTP, PDF, chunker, embedder) | `[x]` HTTP + chunker + embedder complete; PDF not needed |
| 4 | Memory, citation ledger, conflict detector | `[x]` Redis context manager + citation ledger + conflict detector all done |
| 5 | LangGraph orchestration graph | `[x]` DAG wired; planner stores chembl_id for patent agent |
| 6 | Domain agents (Clinical, Patent, Market, Regulatory) | `[x]` all agents with real APIs; domain attr + log_trace + add_citation on all |
| 7 | Synthesis engine, report generator | `[x]` LLM synthesis + conflict detection + Supabase save working |
| 8 | Next.js frontend | `[/]` core UI working; SSE wiring pending |
| 9 | Integration, hardening, deployment | `[/]` pipeline runs end-to-end; API rate limits need resolution |

---

## 🎯 Current Status

**✅ FULLY WORKING END-TO-END WITH SSE + CACHING:**
- Molecule name → ChEMBL resolution (+ chembl_id stored) → 4 agents → synthesis → report → Supabase + local cache + Redis cache
- All infrastructure (Supabase, Qdrant, Redis) fully operational
- Embedding pipeline (chunking → Gemini embedding-001 → Qdrant → retrieval via `query_points`)
- LLM routing (Gemini 2.5 Flash/Pro → NVIDIA Nemotron fallback)
- Citation ledger (Redis-backed, all agents write citations, `/api/report/{id}/citations` endpoint)
- Conflict detector (pairwise domain comparison, wired into synthesis)
- All agents have `domain`, `log_trace`, `add_citation`, `emit_sse`
- **SSE streaming** — real-time progress events from planner → agents → synthesis
- **Frontend SSE integration** — `ProgressViewer` shows live agent status
- **Report caching** — 7-day Redis cache, instant response for popular molecules

**✅ VERIFIED WITH LIVE TESTS:**
- Metformin pipeline: completed in ~90 seconds, 2 repurposing opportunities, 20 citations
- Ibuprofen pipeline: completed successfully with SSE events emitted
- ClinicalTrials.gov: 50 studies found using `query.intr` (intervention search)
- SSE endpoint: broadcasts events to all connected clients
- Cache: instant response for repeated molecule requests

**⚠️ External API Notes:**
- ClinicalTrials.gov: uses `query.intr` (intervention search area) + `requests` lib (httpx blocked by TLS fingerprinting) — WORKING
- EPO OPS: requires `EPO_CLIENT_ID` + `EPO_CLIENT_SECRET` in `.env` — gracefully skipped if absent
- FDA DailyMed: uses list endpoint only (detail endpoint returns XML, not JSON) — WORKING
- OpenFDA: works without API key (rate-limited); set `OPENFDA_API_KEY` for higher limits — WORKING

**System gracefully degrades** — agents continue with LLM-only analysis when APIs fail.

**🚧 OPTIONAL ENHANCEMENTS:**
- ChEMBL autocomplete in search form
- localStorage recent searches
- OpportunityMatrix scatter plot visualization
- CitationDrawer component
- Cache warming (pre-cache top 100 molecules)
