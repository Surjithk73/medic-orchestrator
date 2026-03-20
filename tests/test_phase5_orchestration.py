"""
Phase 5 Tests — LangGraph Orchestration

Verifies:
- State Dict correctly merges values
- Planner correctly populates list of 4 pending domains and resolves canonical
- Dispatcher clears pending tasks and marks them completed
- Replanner correctly identifies when to route to synthesis vs back to queue
- Full graph can execute a smoke test path from start to synthesis
"""

import pytest
import uuid
import warnings

from backend.graph.state import ResearchState, update_dict
from backend.graph.planner import planner_node
from backend.graph.task_queue import task_queue_dispatcher
from backend.graph.replanner import replanner_node
from backend.graph.graph import graph, router_logic

# Filter warning specific to LangGraph StateGraph TypedDict evaluation
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

def test_state_update_dict_logic():
    st1 = {"a": "1"}
    st2 = {"b": "2"}
    merged = update_dict(st1, st2)
    assert "a" in merged and "b" in merged

@pytest.mark.asyncio
async def test_planner_resolves_and_queues():
    session_id = str(uuid.uuid4())
    state: ResearchState = {
        "session_id": session_id,
        "molecule_name": "Tylenol",
        "pending_tasks": [], "completed_tasks": [], "failed_tasks": [],
        "agent_outputs": {}, "all_domains_complete": False, "synthesis_ready": False
    }
    
    res = await planner_node(state)
    assert "clinical" in res["pending_tasks"]
    assert "patent" in res["pending_tasks"]
    assert "market" in res["pending_tasks"]
    assert "regulatory" in res["pending_tasks"]

@pytest.mark.asyncio
async def test_task_queue_dispatcher_execution():
    session_id = str(uuid.uuid4())
    state: ResearchState = {
        "session_id": session_id,
        "molecule_name": "Testing",
        "pending_tasks": ["clinical", "patent"], 
        "completed_tasks": [], "failed_tasks": [],
        "agent_outputs": {}, "all_domains_complete": False, "synthesis_ready": False
    }
    
    res = await task_queue_dispatcher(state)
    assert len(res["pending_tasks"]) == 0
    assert "clinical" in res["completed_tasks"]
    assert "clinical" in res["agent_outputs"]

@pytest.mark.asyncio
async def test_replanner_trigger_synthesis():
    state = {
        "session_id": "test",
        "completed_tasks": ["clinical", "patent", "market", "regulatory"]
    }
    res = await replanner_node(state)
    assert res["synthesis_ready"] is True
    assert res["all_domains_complete"] is True

@pytest.mark.asyncio
async def test_replanner_trigger_requeue():
    state = {
        "session_id": "test",
        "completed_tasks": ["clinical", "patent"] # missing 2
    }
    res = await replanner_node(state)
    assert res["synthesis_ready"] is False
    assert "market" in res["pending_tasks"]

def test_router_edge_logic():
    st_syn = {"synthesis_ready": True}
    res_syn = router_logic(st_syn)
    assert res_syn == "synthesis"
    
    st_q = {"synthesis_ready": False, "pending_tasks": ["market"]}
    res_q = router_logic(st_q)
    assert res_q == "task_queue"

@pytest.mark.asyncio
async def test_full_graph_smoke_test():
    """Execute the full DAG through to Synthesis completion."""
    session_id = str(uuid.uuid4())
    
    # We yield the initial state payload matching the TypedDict keys
    input_payload = {
        "session_id": session_id,
        "molecule_name": "Aspirin",
        "pending_tasks": [],
        "completed_tasks": [],
        "failed_tasks": [],
        "agent_outputs": {},
        "all_domains_complete": False,
        "synthesis_ready": False
    }
    
    # Ainvoke evaluates the entire graph workflow
    final_state = await graph.ainvoke(input_payload)
    
    # We expect planner to add 4, dispatcher to run 4, replanner to flag synthesis, synthesis to cap.
    assert final_state["all_domains_complete"] is True
    assert final_state["synthesis_ready"] is True
    assert len(final_state["completed_tasks"]) == 4
    assert len(final_state["pending_tasks"]) == 0
