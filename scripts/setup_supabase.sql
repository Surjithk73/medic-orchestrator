-- =============================================================================
-- Autonomous Drug Repurposing Intelligence Platform — Supabase Schema
-- Run this once against your Supabase project via the SQL editor or psql.
-- =============================================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ---------------------------------------------------------------------------
-- Research sessions
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  molecule      TEXT NOT NULL,
  canonical     TEXT,
  smiles        TEXT,
  chembl_id     TEXT,
  pubchem_cid   TEXT,
  mechanism     TEXT,
  drug_class    TEXT,
  status        TEXT DEFAULT 'running'
                  CHECK (status IN ('running', 'complete', 'failed')),
  task_graph    JSONB,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  completed_at  TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_molecule ON sessions(molecule);

-- ---------------------------------------------------------------------------
-- Citation ledger — every factual claim → its source
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS citations (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id      UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  claim_text      TEXT NOT NULL,
  domain          TEXT CHECK (domain IN ('clinical','patent','market','regulatory','planner')),
  source_url      TEXT NOT NULL,
  source_title    TEXT,
  source_section  TEXT,
  retrieved_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  confidence      FLOAT DEFAULT 1.0 CHECK (confidence >= 0 AND confidence <= 1),
  flag            TEXT CHECK (flag IN (NULL, 'INFERRED', 'CONFLICTING_SOURCES')),
  chunk_id        TEXT
);

CREATE INDEX IF NOT EXISTS idx_citations_session ON citations(session_id);
CREATE INDEX IF NOT EXISTS idx_citations_domain ON citations(domain);
CREATE INDEX IF NOT EXISTS idx_citations_flag ON citations(flag);

-- ---------------------------------------------------------------------------
-- Final reports
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reports (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id        UUID UNIQUE NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  content_md        TEXT,
  opportunity_matrix JSONB,
  executive_summary TEXT,
  data_gaps         JSONB DEFAULT '[]'::jsonb,
  created_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reports_session ON reports(session_id);

-- ---------------------------------------------------------------------------
-- Agent reasoning traces (debug + explainability)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS agent_traces (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id  UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
  agent       TEXT NOT NULL
                CHECK (agent IN ('clinical','patent','market','regulatory','planner','synthesis','replanner')),
  step        TEXT CHECK (step IN ('query','retrieve','embed','extract','summarise','plan','synthesise')),
  input       JSONB,
  output      JSONB,
  duration_ms INTEGER,
  model_used  TEXT,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_traces_session ON agent_traces(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_traces_agent ON agent_traces(agent);

-- ---------------------------------------------------------------------------
-- EPO response cache (avoid hitting 2500/week limit for same molecule)
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS epo_cache (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  query_key   TEXT UNIQUE NOT NULL,
  response    JSONB NOT NULL,
  cached_at   TIMESTAMPTZ DEFAULT NOW(),
  expires_at  TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '7 days')
);

CREATE INDEX IF NOT EXISTS idx_epo_cache_query ON epo_cache(query_key);
CREATE INDEX IF NOT EXISTS idx_epo_cache_expires ON epo_cache(expires_at);
