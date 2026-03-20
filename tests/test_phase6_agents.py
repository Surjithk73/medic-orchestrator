"""
Phase 6 Tests — Domain Agents

Verifies:
- BaseAgent initialization and trace logging properties
- ClinicalAgent instantiation
- PatentAgent instantiation
- MarketAgent instantiation
- RegulatoryAgent instantiation
"""

import pytest
import uuid

from backend.agents.base import BaseAgent
from backend.agents.clinical import ClinicalAgent
from backend.agents.patent import PatentAgent
from backend.agents.market import MarketAgent
from backend.agents.regulatory import RegulatoryAgent

def test_base_agent_init():
    session_id = str(uuid.uuid4())
    agent = BaseAgent(session_id, "test_domain")
    assert agent.session_id == session_id
    assert agent.domain == "test_domain"

def test_clinical_agent_init():
    agent = ClinicalAgent("sess_123")
    assert agent.domain == "clinical"

def test_patent_agent_init():
    agent = PatentAgent("sess_123")
    assert agent.domain == "patent"

def test_market_agent_init():
    agent = MarketAgent("sess_123")
    assert agent.domain == "market"

def test_regulatory_agent_init():
    agent = RegulatoryAgent("sess_123")
    assert agent.domain == "regulatory"

@pytest.mark.asyncio
async def test_base_agent_methods_exist():
    # Only verify method signature exists to keep tests fast without hitting DB/Redis logic
    agent = BaseAgent("sess", "test")
    assert hasattr(agent, "initialize")
    assert hasattr(agent, "log_trace")
    assert hasattr(agent, "add_citation")
    assert hasattr(agent, "save_summary_for_synthesis")
    assert hasattr(agent, "execute")
