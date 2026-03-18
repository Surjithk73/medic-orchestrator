from backend.graph.state import ResearchState
import asyncio

from backend.agents.clinical import ClinicalAgent
from backend.agents.patent import PatentAgent
from backend.agents.market import MarketAgent
from backend.agents.regulatory import RegulatoryAgent

async def task_queue_dispatcher(state: ResearchState) -> dict:
    """Dispatches tasks to the real domain agents concurrently/synchronously depending on setup."""
    session_id = state["session_id"]
    pending = state.get("pending_tasks", [])
    
    if not pending:
        return {"all_domains_complete": True}
        
    completed = []
    failed = []
    outputs = {}
    
    # Map domains to agent classes
    agent_map = {
        "clinical": ClinicalAgent,
        "patent": PatentAgent,
        "market": MarketAgent,
        "regulatory": RegulatoryAgent
    }
    
    for domain in pending:
        print(f"[{session_id}] Dispatching task: {domain}")
        try:
            agent_class = agent_map.get(domain)
            if agent_class:
                agent = agent_class(session_id)
                res = await agent.execute()
                outputs[domain] = res
                completed.append(domain)
            else:
                failed.append(domain)
        except Exception as e:
            print(f"Agent {domain} execution failed: {e}")
            failed.append(domain)
            
    return {
        "pending_tasks": [],
        "completed_tasks": completed,
        "failed_tasks": failed,
        "agent_outputs": outputs
    }
