from langgraph.graph import StateGraph, END
from backend.graph.state import ResearchState
from backend.graph.planner import planner_node
from backend.graph.task_queue import task_queue_dispatcher
from backend.graph.replanner import replanner_node
from backend.synthesis.cross_domain import synthesis_engine
from backend.synthesis.report_generator import report_generator
from backend.db.supabase_client import update_session_status

async def synthesis_node(state: ResearchState):
    session_id = state['session_id']
    print(f"[{session_id}] Synthesis node running...")
    
    from backend.memory.sse_manager import sse_manager
    await sse_manager.emit(session_id, {
        "event": "synthesis_started",
        "domain": "synthesis",
        "status": "started",
        "message": "Synthesizing cross-domain insights..."
    })
    
    report_data = await synthesis_engine.run_synthesis(session_id)
    await report_generator.finalize_and_save(session_id, report_data)
    await update_session_status(session_id, "complete")
    
    await sse_manager.emit(session_id, {
        "event": "synthesis_complete",
        "domain": "synthesis",
        "status": "completed",
        "message": "Report generated successfully"
    })
    
    return {}

def route_replanner(state: ResearchState):
    if state.get("synthesis_ready"):
        return "synthesis"
    return "task_queue"

builder = StateGraph(ResearchState)

builder.add_node("planner", planner_node)
builder.add_node("task_queue", task_queue_dispatcher)
builder.add_node("replanner", replanner_node)
builder.add_node("synthesis", synthesis_node)

builder.set_entry_point("planner")
builder.add_edge("planner", "task_queue")
builder.add_edge("task_queue", "replanner")
builder.add_conditional_edges("replanner", route_replanner)
builder.add_edge("synthesis", END)

graph = builder.compile()
