"""
Phase 0 Tests — Infrastructure & Configuration

Verifies:
- All required environment variables are present in .env.example
- Qdrant Cloud is reachable and all 4 collections exist
- Supabase is reachable and all 4 tables exist (sessions, citations, reports, agent_traces)
- Upstash Redis is reachable and PING returns PONG
- setup_supabase.sql and setup_qdrant.py scripts are present
"""

import os
import pytest
import httpx
import redis.asyncio as aioredis
from qdrant_client import AsyncQdrantClient
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REQUIRED_ENV_KEYS = [
    "GOOGLE_API_KEY",
    "NCBI_API_KEY",
    "OPENFDA_API_KEY",
    "QDRANT_URL",
    "QDRANT_API_KEY",
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "UPSTASH_REDIS_REST_URL",
    "UPSTASH_REDIS_REST_TOKEN",
    "EPO_CLIENT_ID",
    "EPO_CLIENT_SECRET",
    "DRUGBANK_API_KEY",
    "DEEPSEEK_API_KEY",
]

REQUIRED_QDRANT_COLLECTIONS = [
    "drug_clinical",
    "drug_patent",
    "drug_market",
    "drug_regulatory",
]

REQUIRED_SUPABASE_TABLES = ["sessions", "citations", "reports", "agent_traces"]


# ---------------------------------------------------------------------------
# Phase 0.2 — Environment variables
# ---------------------------------------------------------------------------

def test_env_example_file_exists():
    """The .env.example file must exist at the project root."""
    assert os.path.isfile(".env.example"), ".env.example not found in project root"


def test_env_example_contains_all_required_keys():
    """Every required key must appear in .env.example."""
    with open(".env.example") as f:
        content = f.read()
    missing = [k for k in REQUIRED_ENV_KEYS if k not in content]
    assert not missing, f"Missing keys in .env.example: {missing}"


def test_dotenv_not_committed():
    """The .gitignore must include .env to prevent secret leakage."""
    with open(".gitignore") as f:
        content = f.read()
    assert ".env" in content, ".env not listed in .gitignore"


# ---------------------------------------------------------------------------
# Phase 0.3 — Qdrant connectivity and collections
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_qdrant_reachable():
    """Qdrant Cloud URL should be reachable."""
    url = os.environ["QDRANT_URL"]
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{url}/collections", timeout=10)
    assert resp.status_code == 200, f"Qdrant not reachable: {resp.status_code}"


@pytest.mark.asyncio
async def test_qdrant_collections_exist():
    """All 4 domain collections must exist after running setup_qdrant.py."""
    client = AsyncQdrantClient(
        url=os.environ["QDRANT_URL"],
        api_key=os.environ.get("QDRANT_API_KEY"),
    )
    existing = {c.name for c in (await client.get_collections()).collections}
    missing = [c for c in REQUIRED_QDRANT_COLLECTIONS if c not in existing]
    assert not missing, f"Missing Qdrant collections: {missing}"


@pytest.mark.asyncio
async def test_qdrant_collection_vector_size():
    """Each collection should use 768-dimensional COSINE vectors."""
    client = AsyncQdrantClient(
        url=os.environ["QDRANT_URL"],
        api_key=os.environ.get("QDRANT_API_KEY"),
    )
    for name in REQUIRED_QDRANT_COLLECTIONS:
        info = await client.get_collection(name)
        size = info.config.params.vectors.size
        assert size == 768, f"{name}: expected 768-dim vectors, got {size}"


# ---------------------------------------------------------------------------
# Phase 0.3 — Supabase connectivity and schema
# ---------------------------------------------------------------------------

def test_supabase_reachable():
    """Supabase REST endpoint should respond 200."""
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_ANON_KEY"]
    resp = httpx.get(f"{url}/rest/v1/", headers={"apikey": key}, timeout=10)
    assert resp.status_code in (200, 404), f"Supabase unreachable: {resp.status_code}"


def test_supabase_tables_exist():
    """All 4 required tables must be accessible via Supabase client."""
    sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_ANON_KEY"])
    for table in REQUIRED_SUPABASE_TABLES:
        result = sb.table(table).select("id").limit(1).execute()
        # A 200 with empty data is fine — table exists
        assert result is not None, f"Supabase table missing or inaccessible: {table}"


# ---------------------------------------------------------------------------
# Phase 0.3 — Redis connectivity
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_redis_ping():
    """Upstash Redis should respond to PING with PONG."""
    r = aioredis.from_url(
        os.environ["UPSTASH_REDIS_REST_URL"],
        password=os.environ.get("UPSTASH_REDIS_REST_TOKEN"),
        decode_responses=True,
    )
    result = await r.ping()
    assert result is True, "Redis PING did not return True"


# ---------------------------------------------------------------------------
# Phase 0.3 — Script presence
# ---------------------------------------------------------------------------

def test_setup_scripts_exist():
    """Both setup scripts must be present."""
    assert os.path.isfile("scripts/setup_supabase.sql")
    assert os.path.isfile("scripts/setup_qdrant.py")
