# API Requirements — Autonomous Drug Repurposing Intelligence Platform

> **Every external API the system calls, which module calls it, what it returns, and what credentials are required.**

---

## Summary Table

| # | API | Auth Required | Free? | Used By | Primary Purpose |
|---|-----|--------------|-------|---------|-----------------|
| 1 | ChEMBL REST API | None | ✅ | Planner Node | Molecule identity resolution |
| 2 | DrugBank Open API | API Key (free) | ✅ | Planner Node | Mechanism of action + synonyms |
| 3 | ClinicalTrials.gov v2 | None | ✅ | Clinical Agent | Trial phase, status, indication |
| 4 | PubMed Entrez API | Optional key | ✅ | Clinical Agent | Scientific literature + abstracts |
| 5 | USPTO PatentsView API | None | ✅ | Patent Agent | US patent claims + expiry |
| 6 | EPO Open Patent Services | OAuth 2 (free dev acct) | ✅ | Patent Agent | European patents + legal status |
| 7 | OpenFDA API | Optional key | ✅ | Market Agent + Regulatory Agent | Drug labels, approvals, adverse events |
| 8 | WHO Global Health Observatory | None | ✅ | Market Agent | Disease burden: DALYs, incidence |
| 9 | FDA DailyMed | None | ✅ | Regulatory Agent | Structured product labels |
| 10 | Open Targets GraphQL | None | ✅ | (Optional enrichment) | Disease-target associations |
| 11 | Gemini API (Google AI Studio) | API Key | ✅ | LLM Router, Embedder | LLM inference + text embeddings |
| 12 | DeepSeek API | API Key | ✅ | LLM Router | Fallback LLM (patent + synthesis) |
| 13 | Qdrant Cloud REST | API Key | ✅ | DB Layer | Vector store upsert + search |
| 14 | Supabase REST/PostgREST | Anon Key + Service Role | ✅ | DB Layer | Session, citation, report storage |
| 15 | Upstash Redis REST | REST Token | ✅ | Memory Layer | Entity store, quota counters |

---

## 1. ChEMBL REST API

**Base URL:** `https://www.ebi.ac.uk/chembl/api/data`
**Auth:** None — fully public
**Rate Limit:** Generous public limit (no published number)
**Sign-up Required:** No

**Called By:** `backend/graph/planner.py` — Planner Node

**Endpoints Used:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/molecule?molecule_synonyms__synonym__icontains={name}` | GET | Resolve trade/generic name → canonical molecule |
| `/molecule/{chembl_id}` | GET | Fetch full molecule record by ChEMBL ID |
| `/molecule/search?q={name}` | GET | Synonym expansion fallback when primary query yields no results |

**Response Fields Consumed:**
- `molecule_chembl_id` → stored as `chembl_id`
- `pref_name` → stored as `canonical`
- `molecule_properties.full_molformula`
- `molecule_structures.canonical_smiles` → stored as `smiles`
- `molecule_synonyms[]` → used for alias seeding in Redis entity map
- `cross_references[].xref_id` where `xref_src == "DrugBank"` → DrugBank ID lookup

**Env Variable:** *(none required)*

---

## 2. DrugBank Open API

**Base URL:** `https://go.drugbank.com/structures/v1` (Open Data)  
**Detailed data:** via registered non-commercial API access
**Auth:** API Key (free non-commercial registration at `go.drugbank.com`)
**Sign-up Required:** Yes — 10 minutes

**Called By:** `backend/graph/planner.py` — Planner Node

**Endpoints Used:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/drugs/{drugbank_id}` | GET | Fetch mechanism of action + pharmacological class |
| `/drugs/{drugbank_id}/synonyms` | GET | Full synonym list for alias seeding |

**Response Fields Consumed:**
- `mechanism_of_action` → passed to Planner LLM as molecule context
- `pharmacological_class` → used in query template generation
- `synonyms[]` → all aliases added to Redis entity map at session start

**Env Variable:** `DRUGBANK_API_KEY`

---

## 3. ClinicalTrials.gov v2 REST API

**Base URL:** `https://clinicaltrials.gov/api/v2`
**Auth:** None — fully public
**Rate Limit:** No published limit
**Sign-up Required:** No

**Called By:** `backend/agents/clinical.py` — Clinical Agent

**Endpoints Used:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/studies?query.term={molecule}&pageSize=200&pageToken={token}` | GET | Paginated trial search by molecule name/synonym |
| `/studies/{nct_id}` | GET | Detailed study record for completed trials |

**Response Fields Consumed:**
- `studies[].protocolSection.identificationModule.nctId` → `nct_id`
- `studies[].protocolSection.identificationModule.briefTitle` → `title`
- `studies[].protocolSection.designModule.phases[]` → `phase`
- `studies[].protocolSection.statusModule.overallStatus` → `status`
- `studies[].protocolSection.conditionsModule.conditions[]` → `indication`
- `studies[].protocolSection.outcomesModule.primaryOutcomes[].measure` → `primary_endpoint`
- `studies[].protocolSection.sponsorCollaboratorsModule.leadSponsor.name` → `sponsor`
- `studies[].protocolSection.designModule.enrollmentInfo.count` → `enrollment`
- `studies[].protocolSection.statusModule.startDateStruct.date` → `start_date`
- `studies[].protocolSection.statusModule.completionDateStruct.date` → `completion_date`
- `nextPageToken` → pagination cursor

**Env Variable:** *(none required)*

---

## 4. PubMed Entrez API (NCBI)

**Base URL:** `https://eutils.ncbi.nlm.nih.gov/entrez/eutils`
**Auth:** Optional API Key (triples rate limit: 3 → 10 req/s)
**Rate Limit:** 3 req/s (free), 10 req/s (with key)
**Sign-up Required:** NCBI account at `ncbi.nlm.nih.gov/account` — 3 minutes

**Called By:** `backend/agents/clinical.py` — Clinical Agent

**Endpoints Used:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/esearch.fcgi?db=pubmed&term={query}&retmax=100&api_key={key}` | GET | Search for PubMed article IDs matching the molecule |
| `/efetch.fcgi?db=pubmed&id={pmid_list}&rettype=abstract&retmode=xml&api_key={key}` | GET | Fetch abstract text for matched PMIDs |

**Response Fields Consumed:**
- `esearchresult.idlist[]` → list of PubMed IDs (PMIDs)
- Abstract XML → full text for semantic chunking and embedding

**Env Variable:** `NCBI_API_KEY`

---

## 5. USPTO PatentsView API

**Base URL:** `https://search.patentsview.org/api/v1`
**Auth:** None — fully public
**Rate Limit:** No published limit
**Sign-up Required:** No

**Called By:** `backend/agents/patent.py` — Patent Agent

**Endpoints Used:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/patent/?q={"_text_any":{"patent_abstract":"{molecule}"}}&f=[...]` | GET | Search composition-of-matter + method-of-use patents |
| `/patent/{patent_number}` | GET | Fetch full patent record including claims |

**Request Parameters:**
- `q` — Query JSON (text search on abstract + title)
- `f` — Fields to return (array of field names)
- `o` — Sort order and pagination
- `s` — Sort field

**Response Fields Consumed:**
- `patents[].patent_number` → `patent_number`
- `patents[].patent_title` → `title`
- `patents[].patent_type` → `patent_type`
- `patents[].patent_date` → used to derive `filing_date`
- `patents[].assignees[].assignee_organization` → `assignee`
- `patents[].ipcs[].ipc_class` → `ipc_class`
- `patents[].claims_text` → claim text for LLM extraction + embedding

**Expiry Calculation:** `effective_expiry = filing_date + 20 years` (adjusted per USPTO extension records)

**Env Variable:** *(none required)*

---

## 6. EPO Open Patent Services (OPS)

**Base URL:** `https://ops.epo.org/3.2/rest-services`
**Auth:** OAuth 2.0 Client Credentials (`client_id` + `client_secret`)
**Rate Limit:** 2,500 hits/week (free developer tier)
**Sign-up Required:** Yes — `developers.epo.org` → Create App → 10 minutes

**Called By:** `backend/agents/patent.py` — Patent Agent

**Endpoints Used:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/published-data/search?q={cql_query}` | GET | Search European patents by molecule name |
| `/published-data/publication/{ep_number}/biblio` | GET | Bibliographic data for a specific EP publication |
| `/published-data/publication/{ep_number}/claims` | GET | Full claims text for legal analysis |
| `/legal/{country}/{ep_number}` | GET | Legal status (in force, expired, lapsed) |

**Auth Flow:** `POST https://ops.epo.org/3.2/auth/accesstoken` with `grant_type=client_credentials` → returns `access_token` (Bearer)

**Response Fields Consumed:**
- `ops:world-patent-data.ops:biblio-search.ops:search-result.exchange-documents[]`
  - `patent-number`, `publication-date`, `applicant.applicant-name.name`
  - `classifications-cpc.classification-cpc.text`
- Claims XML → free text for LLM extraction
- Legal status XML → `legal-event-code` (LAPS = lapsed, PGR = granted)

**Env Variables:** `EPO_CLIENT_ID`, `EPO_CLIENT_SECRET`

> **Note:** EPO responses for the same molecule are cached in Supabase to avoid hitting the weekly limit on repeated queries.

---

## 7. OpenFDA API

**Base URL:** `https://api.fda.gov`
**Auth:** Optional API Key (4× rate limit improvement)
**Rate Limit:** 240 req/min (free), 1000 req/min (with key)
**Sign-up Required:** Optional key at `open.fda.gov/apis/authentication`

**Called By:**
- `backend/agents/market.py` — Market Agent (drug labels, approved indications)
- `backend/agents/regulatory.py` — Regulatory Agent (adverse event signals)

**Endpoints Used:**

| Endpoint | Method | Called By | Purpose |
|----------|--------|-----------|---------|
| `/drug/label.json?search=openfda.generic_name:{molecule}&limit=10` | GET | Market Agent | Approved indications + competing products |
| `/drug/event.json?search=patient.drug.medicinalproduct:{molecule}&count=seriousnessother` | GET | Regulatory Agent | Adverse event signal counts |
| `/drug/enforcement.json?search=product_description:{molecule}` | GET | Regulatory Agent | Recall history |

**Response Fields Consumed (Drug Label):**
- `results[].openfda.brand_name[]` → competing products
- `results[].indications_and_usage[]` → approved indications text
- `results[].warnings_and_cautions`, `results[].boxed_warning` → black box warnings
- `results[].openfda.application_number[]` → NDA/BLA numbers

**Response Fields Consumed (Adverse Events):**
- `results[].term` → adverse event term
- `results[].count` → reporting count → used to compute `significant_aes`

**Env Variable:** `OPENFDA_API_KEY`

---

## 8. WHO Global Health Observatory (GHO) API

**Base URL:** `https://ghoapi.azureedge.net/api`
**Auth:** None — fully public
**Rate Limit:** No published limit
**Sign-up Required:** No

**Called By:** `backend/agents/market.py` — Market Agent

**Endpoints Used:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/DALY?$filter=Dim1 eq '{sex}' and Dim2 eq '{region}'` | GET | DALYs by disease, sex, region |
| `/Indicator?$filter=contains(IndicatorName,'daly')` | GET | Discover DALY indicator codes for target indications |
| `/MORT_COUNT?$filter=...` | GET | Mortality counts as disease burden proxy |

**Response Fields Consumed:**
- `value[].NumericValue` → DALY value per 100K population
- `value[].Dim1` / `value[].Dim2` — stratification dimensions
- `value[].TimeDim` → year (use most recent available)

**Mapping:** DALY code → indication name done via WHO indicator metadata

**Env Variable:** *(none required)*

---

## 9. FDA DailyMed API

**Base URL:** `https://dailymed.nlm.nih.gov/dailymed/services/v2`
**Auth:** None — fully public
**Rate Limit:** No published limit
**Sign-up Required:** No

**Called By:** `backend/agents/regulatory.py` — Regulatory Agent

**Endpoints Used:**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/spls.json?drug_name={molecule}` | GET | Search structured product labels by drug name |
| `/spls/{set_id}.json` | GET | Full SPL document for a set ID |
| `/spls/{set_id}/history.json` | GET | Label change history (dates + version summaries) |

**Response Fields Consumed:**
- `data[].setid` → SPL set ID for detailed fetch
- Full SPL JSON → parsed for:
  - `first_approval_year` (from earliest history entry)
  - `label_changes[]` (from history endpoint)
  - `orphan_designations[]` (from SPL sections)
  - `special_designations[]` — Fast-Track, Breakthrough, Accelerated
  - `black_box_warnings[]` (from `BOXED WARNING` section)

**Env Variable:** *(none required)*

---

## 10. Open Targets GraphQL API *(Optional enrichment)*

**Base URL:** `https://api.platform.opentargets.org/api/v4/graphql`
**Auth:** None — fully public
**Rate Limit:** No published limit
**Sign-up Required:** No

**Called By:** `backend/graph/planner.py` (optional enrichment step)

**Query Used:**
```graphql
query($chemblId: String!) {
  drug(chemblId: $chemblId) {
    name
    mechanismsOfAction { rows { actionType mechanismOfAction targets { id approvedSymbol } } }
    indications { rows { disease { id name } maxPhaseForIndication } }
    knownDrugs { rows { disease { name } phase status } }
  }
}
```

**Response Fields Consumed:**
- `indications.rows[]` → existing/in-progress indications with max phase
- `mechanismsOfAction` → target pathways for planner LLM context
- `knownDrugs.rows[]` → competitive landscape for Market Agent context

**Env Variable:** *(none required)*

---

## 11. Google Gemini API (Google AI Studio)

**Base URL:** `https://generativelanguage.googleapis.com/v1beta`
**Auth:** API Key
**Rate Limits (Free Tier):**
- `gemini-2.5-pro`: 5 RPM, 100 RPD
- `gemini-2.5-flash`: 10 RPM, 250 RPD
- `text-embedding-004`: 1500 RPM (very generous)

**Sign-up Required:** Yes — `aistudio.google.com` → 2 minutes, no billing required

**Called By:**
- `backend/graph/planner.py` — Gemini 2.5 Pro (task graph generation)
- `backend/agents/clinical.py`, `market.py`, `regulatory.py` — Gemini 2.5 Flash (structured extraction)
- `backend/synthesis/cross_domain.py` — Gemini 2.5 Pro (synthesis)
- `backend/retrieval/embedder.py` — `text-embedding-004` (all chunk embeddings)

**Models Used:**

| Model ID | Used For | RPM | RPD |
|----------|----------|-----|-----|
| `gemini-2.5-pro-preview-06-05` | Planner, Synthesis | 5 | 100 |
| `gemini-2.5-flash-preview-05-20` | Clinical, Market, Regulatory agents | 10 | 250 |
| `text-embedding-004` | All chunk embedding | 1500 | Unlimited |

**LangChain Integration:** `langchain-google-genai` (`ChatGoogleGenerativeAI`, `GoogleGenerativeAIEmbeddings`)

**Env Variable:** `GOOGLE_API_KEY`

---

## 12. DeepSeek API

**Base URL:** `https://api.deepseek.com/v1`
**Auth:** API Key (Bearer token)
**Rate Limit:** Per plan — free tier available
**Sign-up Required:** Yes — `platform.deepseek.com` → 2 minutes

**Called By:**
- `backend/agents/patent.py` — DeepSeek-V3.1 (primary for technical legal text)
- `backend/synthesis/cross_domain.py` — DeepSeek-R1-0528 (synthesis fallback when Gemini Pro exhausted)

**Models Used:**

| Model ID | Used For |
|----------|----------|
| `deepseek-chat` (maps to V3.1) | Patent agent primary LLM |
| `deepseek-reasoner` (maps to R1-0528) | Synthesis fallback |

**LangChain Integration:** `langchain-community.chat_models.ChatDeepSeek` or direct `httpx` call to OpenAI-compatible endpoint

**Env Variable:** `DEEPSEEK_API_KEY`

---

## 13. Qdrant Cloud REST API

**Base URL:** Your cluster URL (e.g., `https://xyz.us-east4-0.gcp.cloud.qdrant.io`)
**Auth:** API Key
**Free Tier:** 1GB RAM, 4GB disk — no credit card
**Sign-up Required:** Yes — `cloud.qdrant.io` → 5 minutes

**Called By:** `backend/db/qdrant_client.py`

**Operations Used:**

| Operation | Purpose |
|-----------|---------|
| `PUT /collections/{name}` | Create collection (run once via setup script) |
| `PUT /collections/{name}/points` | Upsert embedded chunks |
| `POST /collections/{name}/points/search` | Dense vector similarity search |
| `POST /collections/{name}/points/payload` | BM25-style keyword filter |
| `GET /collections` | Health check + verify all 4 collections exist |

**Collections:** `drug_clinical`, `drug_patent`, `drug_market`, `drug_regulatory`
**Vector params:** 768-dim, COSINE distance

**Env Variables:** `QDRANT_URL`, `QDRANT_API_KEY`

---

## 14. Supabase REST API (PostgREST)

**Base URL:** Your project URL (e.g., `https://xyz.supabase.co`)
**Auth:** Anon Key (public reads) + Service Role Key (server-side writes)
**Free Tier:** 500MB PostgreSQL, forever free
**Sign-up Required:** Yes — `supabase.com` → 5 minutes

**Called By:** `backend/db/supabase_client.py`, `backend/memory/citation_ledger.py`

**Table Operations Used:**

| Table | Operations | Called By |
|-------|-----------|-----------|
| `sessions` | INSERT, SELECT, UPDATE | `supabase_client.py` |
| `citations` | INSERT, SELECT | `citation_ledger.py` |
| `reports` | INSERT, SELECT | `supabase_client.py` |
| `agent_traces` | INSERT | `base.py` (BaseAgent) |

**Python Client:** `supabase-py` v2.x (`from supabase import create_client`)

**Env Variables:** `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`

---

## 15. Upstash Redis REST API

**Base URL:** Your Upstash Redis REST URL (e.g., `https://us1-xxx.upstash.io`)
**Auth:** REST Token (Bearer)
**Free Tier:** 10,000 commands/day
**Sign-up Required:** Yes — `upstash.com` → Select Redis → Free → 3 minutes

**Called By:** `backend/memory/context_manager.py`, `backend/models/llm_router.py`

**Key Patterns Used:**

| Key Pattern | TTL | Used For |
|-------------|-----|---------|
| `session:{id}:status` | Session lifetime | Running/complete status |
| `session:{id}:entity_map` | Session lifetime | Molecule alias → canonical mapping |
| `session:{id}:domain_summaries` | Session lifetime | 4 compressed domain summaries |
| `quota:gemini-pro:rpm_count` | 60s | Per-minute quota tracking |
| `quota:gemini-pro:rpd_count` | Until midnight | Per-day quota tracking |
| `quota:gemini-flash:rpm_count` | 60s | Per-minute quota tracking |
| `quota:gemini-flash:rpd_count` | Until midnight | Per-day quota tracking |

**Operations:** `SET`, `GET`, `INCR`, `EXPIRE`, `HSET`, `HGET`, `HGETALL`, `PING`

**Python Client:** `redis.asyncio` (fully compatible with Upstash REST via URL)

**Env Variables:** `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`

---

## By Agent — Quick Reference

| Agent / Module | APIs Called |
|----------------|-------------|
| **Planner Node** | ChEMBL (#1), DrugBank (#2), Open Targets optional (#10), Gemini Pro (#11) |
| **Clinical Agent** | ClinicalTrials.gov (#3), PubMed Entrez (#4), Gemini Flash (#11), Qdrant (#13) |
| **Patent Agent** | USPTO PatentsView (#5), EPO OPS (#6), DeepSeek V3.1 (#12), Qdrant (#13) |
| **Market Agent** | OpenFDA (#7), WHO GHO (#8), Gemini Flash (#11), Qdrant (#13) |
| **Regulatory Agent** | FDA DailyMed (#9), OpenFDA (#7), Gemini Flash (#11), Qdrant (#13) |
| **Synthesis Engine** | Gemini Pro (#11) primary, DeepSeek R1 (#12) fallback |
| **Embedder** | Gemini text-embedding-004 (#11) |
| **Context Manager** | Upstash Redis (#15), Supabase fallback (#14) |
| **Citation Ledger** | Supabase (#14) |
| **LLM Router** | Upstash Redis (#15) for quota counters |
| **DB Layer** | Qdrant (#13), Supabase (#14) |

---

## Sign-Up Priority Order

Complete these in order before starting Phase 0:

1. **Google AI Studio** — needed for ALL LLM calls and embeddings
2. **Supabase** — needed for session + citation storage (run SQL schema immediately)
3. **Qdrant Cloud** — needed for vector search (run setup script immediately)
4. **Upstash Redis** — needed for quota tracking and entity store
5. **DeepSeek** — needed as LLM fallback
6. **NCBI (PubMed key)** — optional but strongly recommended
7. **OpenFDA key** — optional but strongly recommended
8. **EPO OPS** — needed for European patent data
9. **DrugBank** — needed for synonym expansion + mechanism of action
10. **Azure Student Pack** — needed for production deployment only (can defer)
