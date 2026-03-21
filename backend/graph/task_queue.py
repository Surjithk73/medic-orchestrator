from backend.graph.state import ResearchState
import asyncio

from backend.agents.clinical import ClinicalAgent
from backend.agents.patent import PatentAgent
from backend.agents.market import MarketAgent
from backend.agents.regulatory import RegulatoryAgent

async def task_queue_dispatcher(state: ResearchState) -> dict:
    """Dispatches tasks to the real domain agents concurrently for maximum speed."""
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
    
    print(f"[{session_id}] Dispatching {len(pending)} agents in parallel: {pending}")
    
    # Create agent execution tasks for all pending domains
    async def execute_agent(domain: str):
        """Execute a single agent and return results."""
        try:
            agent_class = agent_map.get(domain)
            if not agent_class:
                return domain, None, "no_agent_class"
            
            agent = agent_class(session_id)
            result = await agent.execute()
            return domain, result, "success"
        except Exception as e:
            print(f"[{session_id}] Agent {domain} execution failed: {e}")
            return domain, None, "failed"
    
    # Run all agents in parallel using asyncio.gather
    tasks = [execute_agent(domain) for domain in pending]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Process results
    for result in results:
        if isinstance(result, Exception):
            print(f"[{session_id}] Agent task raised exception: {result}")
            continue
            
        domain, output, status = result
        
        if status == "success":
            outputs[domain] = output
            completed.append(domain)
            print(f"[{session_id}] ✓ Agent {domain} completed successfully")
        else:
            failed.append(domain)
            print(f"[{session_id}] ✗ Agent {domain} failed with status: {status}")
    
    print(f"[{session_id}] Parallel execution complete: {len(completed)} succeeded, {len(failed)} failed")
            
    return {
        "pending_tasks": [],
        "completed_tasks": completed,
        "failed_tasks": failed,
        "agent_outputs": outputs
    }
