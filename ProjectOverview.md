# Autonomous Drug Repurposing Intelligence Platform

> **One molecule name in. A fully sourced, cross-domain innovation opportunity report out.**
> 

---

## 1. Project Summary

The **Autonomous Drug Repurposing Intelligence Platform** is an AI-powered research system that accepts a single molecule or drug name as input and autonomously orchestrates a multi-domain investigation across clinical trials, patent filings, market intelligence, and regulatory history.

Rather than simply retrieving documents, the system coordinates specialised AI agents that reason about findings across domains and synthesise them into a traceable, structured innovation opportunity report — identifying where an approved molecule may have untapped therapeutic, commercial, or strategic value.

---

## 2. Problem Statement

Pharmaceutical innovation increasingly depends on identifying repurposing opportunities for approved molecules — applying a drug approved for one indication to treat a different condition. This requires navigating an extremely fragmented data ecosystem:

- **Regulatory filings** (FDA, EMA) are buried in PDFs and inconsistent XML
- **Clinical trial data** is structured but requires domain interpretation
- **Patent landscapes** require legal-technical analysis to understand freedom-to-operate
- **Scientific literature** is unstructured, high-volume, and rapidly evolving
- **Market intelligence** is scattered across disease burden databases, approval histories, and competitive pipeline data

Traditional research platforms retrieve documents. They don’t reason about them, don’t connect findings across domains, and don’t produce decision-ready insights. A human analyst doing this work manually takes 2–4 weeks per molecule.

**This system does it autonomously, in minutes, with full source traceability.**

### Key Challenges

| Challenge | Description |
| --- | --- |
| **Research Fragmentation** | Structured data (patents, clinical records) must be integrated with unstructured data (papers, regulatory narratives) without analytical inconsistency |
| **Task Orchestration** | Domain research tasks have epistemic dependencies — patent analysis should be informed by clinical findings; regulatory scanning is shaped by the molecule’s approval history |
| **Traceability** | Every synthesised insight must reference its exact source — a misattributed clinical claim in drug discovery has real consequences |
| **Context Continuity** | Findings from one agent must be visible to others. The system must maintain shared memory across a multi-step research session |
| **Data Heterogeneity** | REST APIs, PDFs, XML label files, and tabular datasets must be normalised into a unified representation before reasoning |
| **Quota Constraints** | All LLM access is on free tiers with per-minute and per-day rate limits — the system must route intelligently and degrade gracefully |

---

## 3. Core Objectives

1. **Accept a molecule name** as the sole user input and resolve it to a canonical identity (canonical name, SMILES string, CAS number, DrugBank ID)
2. **Decompose** the research problem into structured, domain-specific subtasks with explicit dependency ordering
3. **Retrieve** data from at least four independent free data sources per research session in real time
4. **Reason** within each domain using specialised AI agents that produce typed, structured JSON findings
5. **Synthesise** cross-domain findings into unified insights — detecting patent-clinical timeline alignments, unmet needs, and strategic entry windows
6. **Cite** every claim in the output to its original source, section, and retrieval timestamp
7. **Deliver** a formatted innovation opportunity report covering: unmet needs, clinical pipeline status, patent expiry landscape, market potential, and strategic viability

---

## 4. Functional Requirements

### 4.1 Query Handling

- **FR-01** The system shall accept a molecule name in free text (trade name, generic name, or synonym)
- **FR-02** The system shall resolve the input to a canonical molecule identity via ChEMBL API before initiating research
- **FR-03** The system shall support retry with synonym expansion if the primary name yields no results
- **FR-04** The system shall expose a REST API endpoint (`POST /api/research/start`) that initiates the research pipeline and returns a `session_id`

### 4.2 Research Orchestration

- **FR-05** The orchestrator shall decompose each molecule query into a structured task graph with at minimum four domain tasks: Clinical, Patent, Market, Regulatory
- **FR-06** The task graph shall encode explicit dependencies between tasks (e.g., Patent task depends on Clinical findings for indication-targeted patent searches)
- **FR-07** The orchestrator shall support dynamic replanning — issuing new tasks mid-session when a domain agent discovers findings that warrant additional investigation
- **FR-08** All domain agents shall run concurrently where no dependency exists, using async execution

### 4.3 Domain Agents

- **FR-09** The **Clinical Agent** shall query ClinicalTrials.gov v2 and PubMed Entrez and extract: trial phase, status, indication, primary endpoint, NCT ID, sponsor, completion date
- **FR-10** The **Patent Agent** shall query USPTO PatentsView and EPO OPS and extract: patent number, expiry date, claim scope summary, assignee, IPC classification
- **FR-11** The **Market Agent** shall query OpenFDA and WHO GHO and extract: approved indications, competing products, disease burden (DALYs/incidence), unmet need score
- **FR-12** The **Regulatory Agent** shall query FDA DailyMed and OpenFDA adverse events and extract: label history, orphan drug designation, fast-track/breakthrough status, significant safety signals
- **FR-13** Each agent shall output typed JSON conforming to a Pydantic schema — no free-text blobs passed between agents

### 4.4 Retrieval & Memory

- **FR-14** All retrieved text chunks shall be embedded using Gemini `text-embedding-004` and stored in Qdrant with domain-specific collections
- **FR-15** Retrieval shall use hybrid search: BM25 keyword matching AND dense vector similarity, re-ranked by relevance
- **FR-16** The context manager shall maintain a shared entity store in Redis that resolves molecule aliases consistently across all agents
- **FR-17** Every retrieved fact used in reasoning shall be written to the Citation Ledger in Supabase before the synthesis step

### 4.5 Synthesis & Reporting

- **FR-18** The synthesis engine shall produce cross-domain insight analysis covering: gap identification, opportunity scoring on 4 axes, and strategic recommendations
- **FR-19** Every sentence in the synthesis output shall reference at least one `citation_id` from the ledger
- **FR-20** The system shall detect and surface conflicting information between sources, flagging claims as `[CONFLICTING_SOURCES]`
- **FR-21** Claims inferred by the LLM without direct source support shall be flagged as `[INFERRED]`
- **FR-22** The report generator shall produce structured Markdown with domain panels, an opportunity matrix (JSON), and a full citation list

### 4.6 Streaming & User Interface

- **FR-23** Research progress shall be streamed to the frontend via Server-Sent Events (SSE) throughout the pipeline execution
- **FR-24** The frontend shall display a live agent status feed showing which agent is currently running and what it has found
- **FR-25** The report viewer shall provide a citation drawer — clicking any claim opens the source URL, passage, and retrieval metadata
- **FR-26** The frontend shall render an opportunity matrix as a 2×2 chart (axes: clinical evidence strength × commercial potential)

---

## 5. Non-Functional Requirements

### 5.1 Performance

- **NFR-01** A complete research session for a well-documented molecule (e.g., Aspirin, Metformin) shall complete in under 3 minutes
- **NFR-02** The system shall support up to 3 concurrent research sessions without degradation (configurable via `MAX_CONCURRENT_RESEARCH_SESSIONS`)
- **NFR-03** Individual API retrieval calls shall time out at 30 seconds (`RETRIEVAL_TIMEOUT_SECONDS`)

### 5.2 Reliability

- **NFR-04** All LLM calls shall implement exponential backoff with up to 4 retries before falling back to the next model in the fallback chain
- **NFR-05** If a domain agent fails to retrieve data, the pipeline shall continue with the remaining agents and note the failure in the report
- **NFR-06** The system shall not crash if any single external API is unavailable

### 5.3 Traceability

- **NFR-07** 100% of factual claims in the output report shall have a corresponding entry in the Citation Ledger
- **NFR-08** The Citation Ledger shall record: `claim_text`, `source_url`, `source_section`, `retrieved_at`, `confidence`, and `flag`
- **NFR-09** The reasoning trace (which agents ran, in what order, with what intermediate outputs) shall be stored and retrievable per session

### 5.4 Cost

- **NFR-10** The system shall operate at £0/month infrastructure cost using free tiers of all services

### 5.5 Security

- **NFR-11** All API keys shall be stored in environment variables only — never hardcoded or committed to version control
- **NFR-12** The `.env` file shall be listed in `.gitignore` from project initialisation

---

## 6. System Architecture

### 6.1 Architectural Pattern

**Planner-Executor with Contextual RAG and a Shared Citation-Anchored Memory Layer.**

The system is not a simple RAG pipeline (retrieve → embed → summarise). It uses a stateful orchestrator that:
- Builds a dynamic task graph with dependency ordering
- Dispatches domain agents concurrently where possible
- Receives agent findings back into shared state
- Re-evaluates whether new tasks are warranted (replanning)
- Compresses domain summaries before synthesis to manage context window pressure
- Binds every output claim to a citation at generation time

### 6.2 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    USER / FRONTEND                       │
│              POST /api/research/start                    │
│              SSE  /api/research/stream/{id}              │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│              FASTAPI BACKEND (async)                     │
│                                                          │
│  ┌─────────────────────────────────────────────────┐    │
│  │         LANGGRAPH ORCHESTRATION GRAPH           │    │
│  │                                                  │    │
│  │  ┌──────────────────────────────────────────┐   │    │
│  │  │  QUERY DECOMPOSER  (Gemini Flash)         │   │    │
│  │  │  ChEMBL lookup → canonical → task graph  │   │    │
│  │  └────────────────────┬─────────────────────┘   │    │
│  │                       │                          │    │
│  │          ┌────────────▼────────────┐             │    │
│  │          │   DYNAMIC TASK QUEUE    │             │    │
│  │          └──┬──────┬──────┬───────┘             │    │
│  │             │      │      │      │               │    │
│  │    ┌────────▼─┐ ┌──▼───┐ ┌▼─────┐ ┌────────▼─┐ │    │
│  │    │ CLINICAL │ │PATENT│ │MARKET│ │REGULATORY│ │    │
│  │    │  AGENT   │ │AGENT │ │AGENT │ │  AGENT   │ │    │
│  │    └────┬─────┘ └──┬───┘ └──┬───┘ └────┬─────┘ │    │
│  │         │           │        │           │       │    │
│  │    ┌────▼───────────▼────────▼───────────▼────┐  │    │
│  │    │       MEMORY + CONTEXT MANAGER            │  │    │
│  │    │   Redis entity store · Citation Ledger    │  │    │
│  │    │   Conflict detector · Replan triggers     │  │    │
│  │    └────────────────────┬──────────────────────┘  │    │
│  │                         │  (feedback loop)         │    │
│  │                    ┌────▼──────┐                  │    │
│  │                    │ REPLANNER │◄── triggers       │    │
│  │                    └────┬──────┘                  │    │
│  │                         │                          │    │
│  │    ┌────────────────────▼──────────────────────┐  │    │
│  │    │           SYNTHESIS ENGINE                 │  │    │
│  │    │  Gemini Pro / DeepSeek-R1 / Claude Opus   │  │    │
│  │    │  Cross-domain gap analysis · Opportunity  │  │    │
│  │    │  scoring · Citation-anchored output       │  │    │
│  │    └────────────────────┬──────────────────────┘  │    │
│  │                         │                          │    │
│  │    ┌────────────────────▼──────────────────────┐  │    │
│  │    │           REPORT GENERATOR                 │  │    │
│  │    │  Structured Markdown · Opportunity matrix  │  │    │
│  │    │  Citation list · Domain panels             │  │    │
│  │    └───────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ┌──────────────┐  ┌────────────────┐  ┌─────────────┐  │
│  │  Qdrant Cloud│  │Supabase Postgres│  │Upstash Redis│  │
│  │ (4 vector    │  │ citations table │  │ entity store│  │
│  │  collections)│  │ sessions table  │  │ message bus │  │
│  └──────────────┘  └────────────────┘  └─────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 6.3 Orchestration Logic — Who Calls What, When, and Why

```
1. Request arrives → FastAPI creates session record in Supabase
2. LangGraph graph is instantiated with initial state
3. Query Decomposer node runs:
   - Calls ChEMBL API to resolve molecule identity
   - Calls Planner LLM to generate task graph JSON
   - Writes task list to state.task_queue
4. Task Queue dispatcher evaluates dependency graph:
   - Tasks with no dependencies → dispatched concurrently via asyncio.gather()
   - Tasks with dependencies → queued, unblocked when prerequisites complete
5. Each domain agent runs:
   - Calls retrieval APIs (async HTTP with backoff)
   - Embeds retrieved chunks via Gemini text-embedding-004
   - Stores chunks in Qdrant (domain-specific collection)
   - Runs hybrid BM25 + vector retrieval on its own collection
   - Calls executor LLM with retrieved context → extracts typed JSON
   - Writes each finding to Citation Ledger in Supabase
   - Writes compressed 500-token domain summary to shared state
   - Emits SSE progress event to frontend
6. Context Manager runs after each agent completes:
   - Resolves any new entity aliases found
   - Checks for conflicts with prior agent findings
   - Evaluates replan triggers (e.g., "orphan indication found")
7. If replan triggered → Planner node runs again → issues new tasks
8. When all tasks complete → Synthesis Engine node runs:
   - Receives 4 compressed domain summaries (not raw chunks)
   - Calls synthesis LLM (Gemini Pro → DeepSeek-R1 fallback)
   - Outputs opportunity analysis with inline [citation_id] references
9. Report Generator formats output → saves to Supabase reports table
10. SSE completion event sent to frontend → frontend renders report
```

---

## 7. Agent & Module Design

### 7.1 Query Decomposer + Planner

**Responsibility:** Transform a raw molecule name into a structured research plan.

**Inputs:** Raw string (e.g., `"Aspirin"`)

**Process:**
1. Call ChEMBL API: `GET /chembl/api/data/molecule?molecule_synonyms__synonym__icontains=aspirin`
2. Extract: canonical name, SMILES, ChEMBL ID, CAS number, DrugBank cross-reference
3. Call DrugBank API for mechanism of action and pharmacological class
4. Call Planner LLM with molecule context → generate task graph JSON

**Output schema:**

```json
{
  "molecule": {
    "input_name": "Aspirin",
    "canonical": "acetylsalicylic acid",
    "chembl_id": "CHEMBL25",
    "smiles": "CC(=O)Oc1ccccc1C(=O)O",
    "cas": "50-78-2"
  },
  "tasks": [
    {
      "task_id": "t_clinical_01",
      "domain": "clinical",
      "priority": 1,
      "depends_on": [],
      "query_template": "acetylsalicylic acid OR aspirin clinical trials",
      "expected_schema": "ClinicalFinding"
    },
    {
      "task_id": "t_patent_01",
      "domain": "patent",
      "priority": 2,
      "depends_on": ["t_clinical_01"],
      "query_template": "acetylsalicylic acid AND {indication_from_clinical}",
      "expected_schema": "PatentFinding"
    }
  ]
}
```

**Model:** Gemini 2.5 Flash (save Pro quota — this is structured extraction, not deep reasoning)

---

### 7.2 Clinical Analyzer Agent

**Responsibility:** Map the molecule’s clinical evidence landscape across indications.

**Data sources:**
- ClinicalTrials.gov v2 REST API (`/api/v2/studies`)
- PubMed Entrez API (`esearch.fcgi` + `efetch.fcgi`)

**Extracts per trial:**

```python
class ClinicalFinding(BaseModel):
    nct_id: str
    title: str
    phase: str              # Phase 1/2/3/4 or N/A
    status: str             # Recruiting, Completed, Terminated, etc.
    indication: str         # Condition being studied
    primary_endpoint: str
    sponsor: str
    enrollment: int
    start_date: str
    completion_date: str
    source_url: str
    retrieved_at: datetime
```

**Key logic:**
- Searches by molecule canonical name AND major synonyms
- Paginates ClinicalTrials results (max 200 per page)
- Extracts PubMed abstracts for completed trials to get outcome data
- Flags any indication where Phase 2+ evidence exists but no approved indication — this is a repurposing signal

**Model:** DeepSeek-V3.1 or Gemini Flash

---

### 7.3 Patent Reviewer Agent

**Responsibility:** Map the freedom-to-operate landscape and identify patent expiry windows.

**Data sources:**
- USPTO PatentsView API (`/api/v1/patent/`)
- EPO Open Patent Services (`/rest-services/published-data/search`)

**Extracts per patent:**

```python
class PatentFinding(BaseModel):
    patent_number: str
    title: str
    patent_type: str        # composition-of-matter | method-of-use | formulation
    filing_date: str
    expiry_date: str
    assignee: str
    ipc_class: str          # International Patent Classification
    claim_scope_summary: str
    fto_status: str         # clear | blocked | uncertain
    source_url: str
    retrieved_at: datetime
```

**Key logic:**
- Searches composition-of-matter patents (covers the molecule itself)
- Searches method-of-use patents per indication (covers specific applications)
- Calculates effective expiry: filing_date + 20 years, adjusted for extensions
- Cross-references assignee with clinical trial sponsors (same entity = different strategic signal than separate entity)

**Model:** DeepSeek-V3.1 (strong at structured legal text extraction)

---

### 7.4 Market Assessor Agent

**Responsibility:** Estimate commercial opportunity for repurposing candidates.

**Data sources:**
- OpenFDA drug approvals + labeling (`/drug/label/`)
- WHO Global Health Observatory API (`/api/`)

**Extracts:**

```python
class MarketFinding(BaseModel):
    approved_indications: List[str]
    competing_products: List[str]
    disease_burden: Dict[str, float]   # indication → DALY count
    incidence_rate: Dict[str, float]   # indication → per 100K
    unmet_need_score: float            # 0–1, computed heuristic
    competitive_density: str           # low | medium | high
    market_stage: str                  # nascent | growing | mature | declining
    source_urls: List[str]
    retrieved_at: datetime
```

**Key logic:**
- Uses WHO DALYs as market size proxy (free, no license required)
- Computes `unmet_need_score` from: disease burden × (1 - treatment coverage) × (1 / competitive_density)
- Flags indications with high burden + low approved treatments as primary opportunities

**Model:** Gemini 2.5 Flash

---

### 7.5 Regulatory Scanner Agent

**Responsibility:** Identify regulatory history, special designations, and safety constraints.

**Data sources:**
- FDA DailyMed (`https://dailymed.nlm.nih.gov/dailymed/services/v2/`)
- OpenFDA adverse events (`/drug/event/`)

**Extracts:**

```python
class RegulatoryFinding(BaseModel):
    approved_indications: List[str]
    first_approval_year: int
    label_changes: List[Dict]          # Date + change type
    orphan_designations: List[str]
    special_designations: List[str]    # Fast-track, Breakthrough, Accelerated
    black_box_warnings: List[str]
    significant_aes: List[str]         # Adverse events with high reporting rate
    regulatory_pathway_complexity: str # simple | moderate | complex
    source_urls: List[str]
    retrieved_at: datetime
```

**Key logic:**
- Black box warnings constrain repurposing — surface prominently in report
- Orphan designation for a new indication = 7-year market exclusivity in the US
- Fast-track history = regulatory precedent for the molecule’s approvability

**Model:** Gemini 2.5 Flash

---

### 7.6 Memory + Context Manager

**Responsibility:** Shared state, entity resolution, conflict detection, and replan triggering.

**Storage:**
- **Redis (Upstash):** Entity alias map, agent status, message bus between agents
- **Supabase:** Citation ledger (persistent), session state (persistent)

**Entity alias resolution:**

```python
# All of these resolve to the same entity key
aliases = {
    "Aspirin": "acetylsalicylic_acid",
    "Bayer Aspirin": "acetylsalicylic_acid",
    "ASA": "acetylsalicylic_acid",
    "CAS-50-78-2": "acetylsalicylic_acid",
    "CHEMBL25": "acetylsalicylic_acid"
}
```

**Conflict detection:**

```python
# Checks: does finding_B contradict finding_A on the same factual claim?
def detect_conflict(finding_a: dict, finding_b: dict) -> bool:
    # Compare: trial status, patent expiry dates, approval years
    # Flag if same entity, same attribute, different values
```

**Replan triggers:**

```python
REPLAN_TRIGGERS = {
    "orphan_indication_found": lambda f: len(f.get("orphan_designations", [])) > 0,
    "patent_expiry_within_3yr": lambda f: min_expiry_years(f) < 3,
    "phase3_for_new_indication": lambda f: any(t.phase == "Phase 3" for t in f.trials if t.indication not in approved),
    "high_unmet_need_score": lambda f: f.get("unmet_need_score", 0) > 0.75,
}
```

---

### 7.7 Synthesis Engine

**Responsibility:** Cross-domain reasoning, opportunity scoring, and citation-anchored output generation.

**Inputs:** 4 compressed domain summaries (≤500 tokens each) + citation ledger reference

**Opportunity scoring matrix (4 axes, each 0–10):**

| Axis | What It Measures | Data Source |
| --- | --- | --- |
| Clinical Evidence | Strength of existing trial data for repurposing indication | Clinical Agent |
| Freedom to Operate | Patent landscape openness for target indication | Patent Agent |
| Commercial Upside | Disease burden × unmet need × market growth | Market Agent |
| Regulatory Pathway | Complexity / precedent for new indication approval | Regulatory Agent |

**Output format:**

```json
{
  "executive_summary": "Aspirin shows strong repurposing potential for colorectal cancer prevention...",
  "opportunities": [
    {
      "indication": "Colorectal cancer prevention",
      "clinical_score": 7.5,
      "fto_score": 8.0,
      "commercial_score": 8.5,
      "regulatory_score": 6.0,
      "overall_score": 7.5,
      "key_insight": "Phase 3 data [cite:c_021] combined with patent expiry in 2026 [cite:c_047] creates a 3-year entry window",
      "risks": ["Black box warning for GI bleeding [cite:c_088] limits chronic use positioning"],
      "citations": ["c_021", "c_047", "c_088"]
    }
  ],
  "strategic_recommendations": [...],
  "data_gaps": ["No Phase 2 data found for Alzheimer's indication — recommend manual search"]
}
```

**Model:** Gemini 2.5 Pro → DeepSeek-R1-0528 → Claude Opus (when available)

---

## 8. Data Sources

All data sources below are **free to access**, require no credit card, and are used in compliance with their terms of service for non-commercial research purposes.

| Source | Type | Data Provided | Auth | Rate Limit |
| --- | --- | --- | --- | --- |
| ClinicalTrials.gov v2 | REST API | 570K+ trials: phase, status, indication, endpoints | None required | No published limit |
| PubMed Entrez | REST API | Scientific literature search + abstracts | Optional key (recommended) | 3 req/s free; 10 req/s with key |
| OpenFDA | REST API | Drug labels, adverse events, approvals | Optional key (recommended) | 240 req/min free; 1000/min with key |
| ChEMBL | REST API | Bioactivity, targets, compound identity | None | Generous public limit |
| Open Targets | GraphQL API | Disease-target associations, evidence | None | No published limit |
| USPTO PatentsView | REST API | US patents: claims, assignee, expiry | None | No published limit |
| EPO OPS | REST API | European patents, legal status | Free developer account | 2500 hits/week |
| WHO GHO | REST API | Disease burden: DALYs, incidence | None | No published limit |
| DrugBank Open | REST API | Drug synonyms, mechanism, PK data | Free non-commercial registration | Moderate |
| FDA DailyMed | REST API | Structured product labels | None | No published limit |

### 8.1 Handling Structured vs Unstructured Data

**Structured data** (ClinicalTrials JSON, PatentsView JSON, OpenFDA JSON):
- Parse directly into Pydantic models
- No embedding needed for exact field lookups
- Embed free-text fields (title, description, claim text) for semantic retrieval

**Unstructured data** (PubMed abstracts, regulatory PDF narratives):
- PyMuPDF for PDF text extraction
- pdfplumber for table extraction within PDFs
- Chunk by semantic boundary (section headers, paragraph breaks) — NOT fixed token windows
- Embed with Gemini text-embedding-004 → store in Qdrant

---

## 9. Data Flow

```
INPUT: "Aspirin"
    │
    ▼
[Query Decomposer]
    ├── ChEMBL API → canonical: "acetylsalicylic acid", chembl_id: CHEMBL25
    ├── DrugBank API → mechanism: COX inhibitor, class: NSAID
    └── Planner LLM → task_graph.json (4 tasks, dependency order)
    │
    ▼
[Task Queue] ─── dispatches concurrently ──────────────────────┐
    │                                                           │
    ▼                                                           ▼
[Clinical Agent]                                    [Market + Regulatory Agents]
    ├── ClinicalTrials.gov API → 47 trials found   (run in parallel)
    ├── PubMed API → 120 abstracts retrieved
    ├── Embed chunks → Qdrant[drug_clinical]
    ├── Hybrid retrieval → top 20 chunks
    ├── DeepSeek-V3.1 → ClinicalFinding[] JSON
    ├── Write 20 citation rows → Supabase
    └── Write 500-token summary → shared state
    │
    ▼ (clinical complete → unblocks Patent Agent)
[Patent Agent]
    ├── PatentsView API → query uses indication from clinical findings
    ├── EPO OPS API → European counterparts
    ├── Embed claim text → Qdrant[drug_patent]
    ├── DeepSeek-V3.1 → PatentFinding[] JSON
    ├── Write citation rows → Supabase
    └── Write 500-token summary → shared state
    │
    ▼
[Context Manager]
    ├── Resolve aliases across all agents
    ├── Detect conflicts (e.g., two sources disagree on trial status)
    ├── Evaluate replan triggers
    └── (if triggered) → Planner issues new task → cycle repeats
    │
    ▼
[Synthesis Engine] (receives 4 × 500-token summaries)
    ├── Gemini 2.5 Pro → cross-domain analysis
    ├── Inline [citation_id] references at claim level
    ├── Opportunity scoring matrix JSON
    └── Strategic recommendations
    │
    ▼
[Report Generator]
    ├── Structured Markdown report
    ├── Opportunity matrix (JSON for frontend chart)
    ├── Full citation list with URLs
    └── Save to Supabase reports table
    │
    ▼
OUTPUT: Innovation Opportunity Report (with live SSE streaming throughout)
```

---

## 10. LLM Strategy

### 10.1 Model Routing

| Component | Primary Model | Fallback 1 | Fallback 2 | Reason |
| --- | --- | --- | --- | --- |
| Planner / Orchestrator | Gemini 2.5 Pro | DeepSeek-R1-0528 | Hunter Alpha | Needs highest reasoning quality; complex task graph generation |
| Clinical Agent | Gemini 2.5 Flash | DeepSeek-V3.1 | Hunter Alpha | Fast structured extraction; flash is sufficient |
| Patent Agent | DeepSeek-V3.1 | Gemini 2.5 Flash | Hunter Alpha | Strong at technical legal text parsing |
| Market Agent | Gemini 2.5 Flash | DeepSeek-V3.1 | Hunter Alpha | Simple structured extraction |
| Regulatory Agent | Gemini 2.5 Flash | DeepSeek-V3.1 | Hunter Alpha | Simple structured extraction |
| Synthesis Engine | Gemini 2.5 Pro | DeepSeek-R1-0528 | Claude Opus | Highest quality — this is where reasoning quality matters most |
| Embeddings | Gemini text-embedding-004 | — | — | Only free high-quality embedding on the same API |

### 10.2 Quota Management

**Gemini 2.5 Pro:** 5 RPM, 100 RPD (free tier)
- With 2 Pro calls per session (Planner + Synthesis), supports ~50 sessions/day
- Implement request counting in Redis — block new Pro calls if within 10 of daily limit

**Gemini 2.5 Flash:** 10 RPM, 250 RPD (free tier)
- 4 agent calls per session = ~60 sessions/day before hitting daily limit
- Fall back to DeepSeek-V3.1 for executors after 200 Flash calls

**Fallback chain implementation:**

```python
# backend/models/llm_router.py
PLANNER_CHAIN = [
    ("gemini-2.5-pro-preview", 5),      # RPM limit
    ("deepseek-reasoner", 10),
    ("hunter-alpha-unlimited", None),
]

async def call_with_fallback(chain: list, prompt: str, schema: BaseModel):
    for model_name, rpm_limit in chain:
        try:
            if await quota_available(model_name, rpm_limit):
                return await call_llm(model_name, prompt, schema)
        except (RateLimitError, QuotaExceededError):
            continue
    raise AllModelsExhaustedException()
```

### 10.3 Context Window Management

Each agent produces a **compressed 500-token summary** before the synthesis step. The synthesis engine receives only these summaries, never the raw retrieved chunks. This prevents context overflow while preserving the key findings.

Raw chunks and their embeddings remain accessible in Qdrant and the Citation Ledger for traceability — they just don’t enter the synthesis prompt.

---

## 11. Tech Stack

### 11.1 Backend

| Component | Technology | Version | Why |
| --- | --- | --- | --- |
| Runtime | Python | 3.11+ | Best LLM library ecosystem |
| API Framework | FastAPI | 0.115+ | Native async, SSE support, auto OpenAPI docs |
| ASGI Server | Uvicorn | Latest | High-performance async server |
| Orchestration | LangGraph | 0.2+ | Stateful directed graph, conditional branching |
| LLM Abstraction | LangChain | 0.3+ | Model-agnostic — swap providers without rewriting agents |
| HTTP Client | httpx | Latest | Async HTTP with timeout and retry support |
| Data Validation | Pydantic v2 | 2.x | Typed schemas between agents |
| PDF Parsing | PyMuPDF (fitz) | Latest | Fastest PDF text extraction |
| Table Extraction | pdfplumber | Latest | Best for regulatory document tables |

### 11.2 Frontend

| Component | Technology | Why |
| --- | --- | --- |
| Framework | Next.js 14 (App Router) | File-based routing, SSE-friendly, Vercel deploy |
| Styling | TailwindCSS | Rapid UI, no CSS bundle overhead |
| Charts | Recharts | React-native, no extra bundle cost |
| SSE | Custom `useSSE` hook | Native browser EventSource API — no library needed |
| State | React Context + useState | Simple enough — no Redux needed |
| Icons | Lucide React | Free, tree-shakeable |

### 11.3 Infrastructure (All Free)

| Service | Provider | Free Tier | Use |
| --- | --- | --- | --- |
| Vector DB | Qdrant Cloud | 1GB RAM, 4GB disk, no credit card | 4 domain embedding collections |
| Relational DB | Supabase | 500MB PostgreSQL, forever free | Sessions, citations, reports |
| Cache / Bus | Upstash Redis | 10K commands/day, free | Entity store, message bus, quota counters |
| Backend hosting | Azure Container Apps | $100 Student Pack credit | FastAPI container, serverless |
| Frontend hosting | Vercel | Unlimited hobby projects | Next.js, global CDN |
| CI/CD | GitHub Actions | 2000 min/month (Student Pack) | Build + deploy on push |
| LLM tracing | LangSmith | Free tier | Debug agent reasoning chains |

### 11.4 Python Dependencies

```
# requirements.txt
fastapi==0.115.0
uvicorn[standard]==0.30.0
langgraph==0.2.0
langchain==0.3.0
langchain-google-genai==2.0.0
langchain-community==0.3.0
httpx==0.27.0
pydantic==2.8.0
qdrant-client==1.11.0
supabase==2.7.0
redis==5.0.8
PyMuPDF==1.24.0
pdfplumber==0.11.0
python-dotenv==1.0.1
langsmith==0.1.0
tenacity==9.0.0          # Retry logic with exponential backoff
```

---

## 12. Database Schema

### 12.1 Supabase (PostgreSQL)

```sql
-- Research sessions
CREATE TABLE sessions (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  molecule      TEXT NOT NULL,           -- Raw input
  canonical     TEXT,                    -- Resolved canonical name
  smiles        TEXT,                    -- SMILES string
  chembl_id     TEXT,                    -- ChEMBL identifier
  status        TEXT DEFAULT 'running',  -- running | complete | failed
  task_graph    JSONB,                   -- Full task dependency graph
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  completed_at  TIMESTAMPTZ
);

-- Citation ledger — every claim → every source
CREATE TABLE citations (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id      UUID REFERENCES sessions(id) ON DELETE CASCADE,
  claim_text      TEXT NOT NULL,         -- The specific claim being cited
  domain          TEXT,                  -- clinical | patent | market | regulatory
  source_url      TEXT NOT NULL,
  source_title    TEXT,
  source_section  TEXT,                  -- Section within source doc
  retrieved_at    TIMESTAMPTZ NOT NULL,
  confidence      FLOAT DEFAULT 1.0,     -- Agent confidence in this source
  flag            TEXT,                  -- NULL | INFERRED | CONFLICTING
  chunk_id        TEXT                   -- Qdrant chunk ID for traceability
);

-- Final reports
CREATE TABLE reports (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id        UUID REFERENCES sessions(id) UNIQUE,
  content_md        TEXT,                -- Full Markdown report
  opportunity_matrix JSONB,              -- 4-axis scoring per indication
  executive_summary TEXT,
  data_gaps         JSONB,               -- List of knowledge gaps
  created_at        TIMESTAMPTZ DEFAULT NOW()
);

-- Agent reasoning trace (for debugging + explainability)
CREATE TABLE agent_traces (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id  UUID REFERENCES sessions(id) ON DELETE CASCADE,
  agent       TEXT NOT NULL,             -- clinical | patent | market | regulatory | planner
  step        TEXT,                      -- query | retrieve | embed | extract | summarise
  input       JSONB,
  output      JSONB,
  duration_ms INTEGER,
  model_used  TEXT,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);
```

### 12.2 Qdrant Collections

```python
# 4 separate collections — domain-specific embedding spaces
collections = [
    CollectionConfig(
        name="drug_clinical",
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    ),
    CollectionConfig(
        name="drug_patent",
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    ),
    CollectionConfig(
        name="drug_market",
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    ),
    CollectionConfig(
        name="drug_regulatory",
        vectors_config=VectorParams(size=768, distance=Distance.COSINE),
    ),
]

# Each point payload schema
payload = {
    "session_id": "uuid",
    "molecule": "acetylsalicylic acid",
    "source_url": "https://clinicaltrials.gov/...",
    "source_section": "Abstract",
    "chunk_text": "...",
    "retrieved_at": "2026-03-19T12:00:00Z",
    "citation_id": "uuid"  # Links back to Supabase citations table
}
```

### 12.3 Redis Keys (Upstash)

```
session:{session_id}:status          → "running" | "complete"
session:{session_id}:entity_map      → JSON alias → canonical mapping
session:{session_id}:domain_summaries → JSON {clinical: ..., patent: ...}
quota:gemini-pro:rpm_count           → integer (expires every 60s)
quota:gemini-pro:rpd_count           → integer (expires at midnight)
quota:gemini-flash:rpm_count         → integer
quota:gemini-flash:rpd_count         → integer
```

---

## 13. API Reference

### 13.1 Backend Endpoints

### `POST /api/research/start`

Initiates a new research session.

**Request:**

```json
{ "molecule": "Aspirin" }
```

**Response:**

```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "canonical": "acetylsalicylic acid",
  "estimated_duration_seconds": 120
}
```

---

### `GET /api/research/stream/{session_id}`

Server-Sent Events stream of research progress.

**Events:**

```
event: agent_started
data: {"agent": "clinical", "message": "Querying ClinicalTrials.gov..."}

event: agent_complete
data: {"agent": "clinical", "findings_count": 47, "citations_added": 23}

event: replan
data: {"reason": "orphan_indication_found", "new_tasks": ["t_regulatory_02"]}

event: synthesis_started
data: {"message": "Cross-domain analysis in progress..."}

event: complete
data: {"report_id": "uuid", "redirect": "/report/uuid"}
```

---

### `GET /api/report/{session_id}`

Retrieve completed report.

**Response:**

```json
{
  "session_id": "uuid",
  "molecule": "acetylsalicylic acid",
  "status": "complete",
  "report": {
    "executive_summary": "...",
    "opportunity_matrix": [...],
    "domain_panels": {
      "clinical": { "summary": "...", "findings": [...], "citation_count": 23 },
      "patent": { "summary": "...", "findings": [...], "citation_count": 18 },
      "market": { "summary": "...", "findings": [...], "citation_count": 11 },
      "regulatory": { "summary": "...", "findings": [...], "citation_count": 14 }
    },
    "strategic_recommendations": [...],
    "data_gaps": [...]
  }
}
```

---

### `GET /api/citations/{session_id}`

Retrieve full citation ledger for a session.

**Response:**

```json
{
  "citations": [
    {
      "id": "c_021",
      "claim_text": "Aspirin Phase 3 trial for colorectal cancer prevention completed 2024",
      "domain": "clinical",
      "source_url": "https://clinicaltrials.gov/study/NCT04767867",
      "source_title": "ASPIRIN-CRC Phase 3 Trial",
      "source_section": "Results",
      "retrieved_at": "2026-03-19T10:23:00Z",
      "confidence": 0.97,
      "flag": null
    }
  ]
}
```

---

## 14. Frontend Design

### 14.1 Pages

**`/` — Molecule Search**
- Centred search input with molecule name placeholder
- Autocomplete powered by ChEMBL API as-you-type
- Recent searches (localStorage)
- Background: subtle molecular structure SVG pattern

**`/research/[session_id]` — Live Research Progress**
- Four agent status cards (Clinical, Patent, Market, Regulatory) with live status badges
- Timeline feed showing SSE events as they arrive
- Expandable “reasoning trace” panel showing what each agent is actually doing
- Spinning indicators on active agents, checkmarks on complete

**`/report/[session_id]` — Report Viewer**
- Fixed left panel: 4 domain tabs (Clinical | Patent | Market | Regulatory) + Opportunity Matrix tab
- Main content: rendered Markdown with inline `[cite:c_021]` links
- Clicking a citation link opens a right drawer showing:
- Source title, URL, section
- Retrieved passage (the exact chunk used)
- Retrieval timestamp + confidence score
- Opportunity Matrix: 2×2 scatter chart (Recharts) with indication bubbles
- X-axis: Commercial Potential (0–10)
- Y-axis: Clinical Evidence (0–10)
- Bubble size: FTO score
- Bubble colour: Regulatory complexity (green/amber/red)

### 14.2 SSE Hook

```tsx
// hooks/useSSE.ts
export function useSSE(sessionId: string) {
  const [events, setEvents] = useState<ResearchEvent[]>([]);
  const [complete, setComplete] = useState(false);

  useEffect(() => {
    const source = new EventSource(`/api/research/stream/${sessionId}`);

    source.addEventListener('agent_complete', (e) => {
      setEvents(prev => [...prev, JSON.parse(e.data)]);
    });

    source.addEventListener('complete', (e) => {
      setComplete(true);
      source.close();
    });

    return () => source.close();
  }, [sessionId]);

  return { events, complete };
}
```

---

## 15. Traceability & Citation System

### 15.1 Philosophy

Every factual claim in the output must be traceable to its source. The system enforces this at generation time — not as a post-hoc check — by requiring the synthesis LLM to include `[cite:citation_id]` inline for every claim, where `citation_id` must exist in the Citation Ledger before the synthesis prompt runs.

### 15.2 Citation Ledger Flow

```
1. Agent retrieves chunk from API or PDF
2. Agent writes citation row to Supabase BEFORE using the chunk in reasoning
   → citation_id is generated at this point
3. Agent passes citation_ids alongside chunk text to LLM
4. LLM includes [cite:c_021] in output when using that chunk
5. Synthesis engine receives domain summaries with embedded citation IDs
6. Synthesis output inherits citation IDs from domain summaries
7. Report generator resolves citation IDs → full source metadata
8. Frontend renders [cite:c_021] as clickable link → opens citation drawer
```

### 15.3 Conflict Handling

When the Context Manager detects that two sources report conflicting facts about the same entity and attribute:

1. Both citations are retained in the ledger
2. The claim is flagged as `CONFLICTING_SOURCES`
3. Both source URLs are surfaced in the report
4. The synthesis engine is explicitly prompted: *“Two sources disagree on this point — present both and do not resolve the conflict”*

### 15.4 Inference Flagging

If the synthesis engine draws a conclusion that goes beyond the direct evidence (a necessary step in cross-domain reasoning), the claim is tagged `[INFERRED]`. This tells a human reviewer that the claim is a model inference, not a direct citation, and warrants additional verification.

---

## 16. Environment Configuration

The `.env.example` file included in this project contains all required environment variables with inline documentation. Copy it to `.env` and fill in your actual keys.

### 16.1 Services Requiring Sign-Up (All Free)

| Service | URL | Time to Set Up | Notes |
| --- | --- | --- | --- |
| Google AI Studio (Gemini) | aistudio.google.com | 2 minutes | No billing required for free tier |
| NCBI (PubMed key) | ncbi.nlm.nih.gov/account | 3 minutes | Triples rate limit for free |
| OpenFDA key | open.fda.gov/apis/authentication | 2 minutes | 4× rate limit improvement |
| Qdrant Cloud | cloud.qdrant.io | 5 minutes | No credit card required |
| Supabase | supabase.com | 5 minutes | Run `scripts/setup_supabase.sql` after |
| Upstash Redis | upstash.com | 3 minutes | Select “Redis” → free tier |
| EPO Developer | developers.epo.org | 10 minutes | Create app → get client_id + secret |
| DrugBank Open | go.drugbank.com | 10 minutes | Non-commercial registration |
| DeepSeek | platform.deepseek.com | 2 minutes | Already have access |
| Azure (Student Pack) | education.github.com/pack | 15 minutes | Activate Student Pack first |

**Total setup time: ~60 minutes, £0 spent.**

### 16.2 Services With No Sign-Up Required

ClinicalTrials.gov · ChEMBL · Open Targets · USPTO PatentsView · WHO GHO · FDA DailyMed

These are called directly — no key, no account, no rate limit registration needed.

---

## 17. Project Structure

```
drug-repurposing-platform/
│
├── .env.example                     # Complete environment template (this repo)
├── .env                             # Your filled-in secrets — NEVER COMMIT
├── .gitignore                       # Includes .env, __pycache__, .next
├── docker-compose.yml               # Local dev: backend + Redis
├── Dockerfile                       # Backend container for Azure
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
│
├── scripts/
│   ├── setup_qdrant.py              # Creates 4 Qdrant collections
│   └── setup_supabase.sql           # Creates all DB tables
│
├── backend/
│   ├── main.py                      # FastAPI app: routes, SSE, lifecycle
│   │
│   ├── graph/                       # LangGraph orchestration
│   │   ├── state.py                 # TypedDict: molecule, tasks, findings, citations
│   │   ├── graph.py                 # Full graph definition with edges + conditionals
│   │   ├── planner.py               # Planner node (Gemini Pro)
│   │   ├── task_queue.py            # Async task dispatcher
│   │   └── replanner.py             # Conditional replanning logic
│   │
│   ├── agents/                      # Domain executor agents
│   │   ├── base.py                  # BaseAgent with retry, logging, SSE emit
│   │   ├── clinical.py              # ClinicalTrials.gov + PubMed
│   │   ├── patent.py                # PatentsView + EPO OPS
│   │   ├── market.py                # OpenFDA + WHO GHO
│   │   └── regulatory.py            # DailyMed + OpenFDA adverse events
│   │
│   ├── retrieval/                   # Data access layer
│   │   ├── api_client.py            # Async HTTP with exponential backoff
│   │   ├── pdf_parser.py            # PyMuPDF + pdfplumber pipeline
│   │   ├── chunker.py               # Semantic chunking (not fixed-size)
│   │   └── embedder.py              # Gemini text-embedding-004 wrapper
│   │
│   ├── memory/                      # Shared state and persistence
│   │   ├── context_manager.py       # Redis entity store + alias resolution
│   │   ├── citation_ledger.py       # Supabase citation CRUD
│   │   └── conflict_detector.py     # Cross-agent fact conflict checking
│   │
│   ├── synthesis/
│   │   ├── cross_domain.py          # Gap analysis + opportunity scoring
│   │   └── report_generator.py      # Markdown report formatter
│   │
│   ├── db/
│   │   ├── qdrant_client.py         # Collection management + upsert + search
│   │   └── supabase_client.py       # Session + citation + report operations
│   │
│   └── models/
│       ├── llm_router.py            # Fallback chain: Gemini → DeepSeek → Hunter
│       └── schemas.py               # Pydantic output schemas for every agent
│
└── frontend/
    ├── app/
    │   ├── page.tsx                 # Molecule search page
    │   ├── research/
    │   │   └── [session_id]/
    │   │       └── page.tsx         # Live research progress
    │   └── report/
    │       └── [session_id]/
    │           └── page.tsx         # Report viewer
    │
    ├── components/
    │   ├── MoleculeSearch.tsx        # Autocomplete search input
    │   ├── ResearchProgress.tsx      # Live SSE event feed + agent cards
    │   ├── ReasoningTrace.tsx        # Expandable agent thought chain
    │   ├── OpportunityMatrix.tsx     # 2×2 Recharts scatter plot
    │   ├── CitationDrawer.tsx        # Slide-in source panel
    │   ├── DomainPanel.tsx           # Per-domain findings with citations
    │   └── ReportViewer.tsx          # Full report with all panels
    │
    └── hooks/
        └── useSSE.ts                # EventSource hook for streaming
```

---

### What to Simulate vs Build Fully

| Feature | Build Fully | Simulate / Stub |
| --- | --- | --- |
| ClinicalTrials.gov retrieval | ✅ |  |
| OpenFDA retrieval | ✅ |  |
| Gemini embedding + Qdrant | ✅ |  |
| Citation ledger | ✅ |  |
| SSE streaming | ✅ |  |
| Patent expiry calculation | ✅ |  |
| Market financial projections |  | ✅ Use WHO DALY data as proxy |
| EMA PDF scraping |  | ✅ Use local sample 5-10 PDFs |
| Full replanning loop |  | ✅ Hard-code 2-3 trigger conditions |
| Multi-molecule batch |  | ✅ Single molecule only for MVP |

---

## 19. Failure Modes & Mitigations

| Failure Mode | Risk | Mitigation |
| --- | --- | --- |
| Gemini Pro quota exhausted mid-session | High | Track RPD in Redis; fall back to DeepSeek-R1 automatically |
| ClinicalTrials.gov returns 0 results | Medium | Retry with synonym expansion from DrugBank; continue without clinical if all retries fail |
| EPO OPS weekly limit hit | Medium | Cache EPO responses in Supabase; serve cached results for same molecule |
| LLM hallucinates a source URL | High | Require LLM to cite only `citation_id`s that already exist in ledger; validate before report generation |
| LLM makes false cross-domain connection | High | Require explicit dual-citation for cross-domain claims; flag single-source cross-domain inferences as `[INFERRED]` |
| Context window overflow on molecule with 500+ trials | Medium | Hard cap at `MAX_CHUNKS_PER_DOMAIN=20`; always use compressed 500-token domain summaries for synthesis |
| Entity resolution failure | Medium | Maintain known-alias seeding from DrugBank at session start; log unresolved aliases for manual review |
| PDF parsing fails on scanned regulatory doc | Low | Detect scanned PDF (no text layer) → skip with data gap note; continue session |
| Upstash Redis 10K command limit hit | Low | Batch Redis operations; use Supabase as fallback for entity store |
| Supabase 500MB limit approached | Very Low | Citations are small rows; 500MB supports ~5M citation records |

---