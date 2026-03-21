from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import uuid
import asyncio
import json

from backend.db.supabase_client import create_session
from backend.graph.graph import graph
from backend.memory.sse_manager import sse_manager
from backend.memory.report_cache import report_cache
from backend.graph.planner import planner_node
from backend.graph.state import ResearchState

router = APIRouter()

class ResearchStartRequest(BaseModel):
    molecule: str = Field(..., description="The name of the molecule or drug to investigate.")
    force_refresh: bool = Field(False, description="Force re-run even if cached report exists")

class ResearchStartResponse(BaseModel):
    session_id: str
    status: str
    canonical: str | None = None
    estimated_duration_seconds: int = 120
    from_cache: bool = False

async def enqueue_research_pipeline(session_id: str, molecule: str):
    """Triggers the LangGraph agent chain in the background on the main event loop."""
    print(f"[{session_id}] Background dispatching pipeline for {molecule}...")
    
    payload = {
        "session_id": str(session_id),
        "molecule_name": molecule,
        "pending_tasks": [],
        "completed_tasks": [],
        "failed_tasks": [],
        "agent_outputs": {},
        "all_domains_complete": False,
        "synthesis_ready": False
    }
    
    try:
        await graph.ainvoke(payload)
    except Exception as e:
        print(f"[{session_id}] Graph execution failed: {e}")
        await sse_manager.emit(session_id, {
            "event": "error",
            "domain": "system",
            "status": "failed",
            "message": str(e)
        })

@router.post("/start", response_model=ResearchStartResponse)
async def start_research(payload: ResearchStartRequest):
    molecule = payload.molecule.strip()
    if not molecule:
        raise HTTPException(status_code=422, detail="Molecule name cannot be empty")
    
    try:
        from backend.memory.context_manager import context_manager

        # --- Fast cache check BEFORE running planner ---
        # Try the raw input name first (handles exact matches like "Thalidomide")
        if not payload.force_refresh:
            cached_report = await report_cache.get(molecule)
            if cached_report:
                session_id = await create_session(molecule=molecule)
                import os
                os.makedirs("tmp_reports", exist_ok=True)
                with open(f"tmp_reports/{session_id}.json", "w") as f:
                    json.dump(cached_report, f, indent=2)
                print(f"[{session_id}] Fast cache hit for raw name: {molecule}")
                return ResearchStartResponse(
                    session_id=str(session_id),
                    status="complete",
                    canonical=molecule,
                    estimated_duration_seconds=0,
                    from_cache=True
                )

        # No fast cache hit — resolve canonical name via planner
        temp_state: ResearchState = {
            "session_id": "temp",
            "molecule_name": molecule,
            "pending_tasks": [],
            "completed_tasks": [],
            "failed_tasks": [],
            "agent_outputs": {},
            "all_domains_complete": False,
            "synthesis_ready": False
        }
        
        await context_manager.set_session_entity("temp", {})
        planner_result = await planner_node(temp_state)
        canonical_name = planner_result.get("molecule_name", molecule)
        
        # Check cache again with resolved canonical name (if different from raw input)
        if not payload.force_refresh and canonical_name.upper() != molecule.upper():
            cached_report = await report_cache.get(canonical_name)
            if cached_report:
                session_id = await create_session(molecule=molecule)
                import os
                os.makedirs("tmp_reports", exist_ok=True)
                with open(f"tmp_reports/{session_id}.json", "w") as f:
                    json.dump(cached_report, f, indent=2)
                print(f"[{session_id}] Cache hit for canonical name: {canonical_name}")
                return ResearchStartResponse(
                    session_id=str(session_id),
                    status="complete",
                    canonical=canonical_name,
                    estimated_duration_seconds=0,
                    from_cache=True
                )
        
        # No cache — run full pipeline
        session_id = await create_session(molecule=molecule)
        asyncio.create_task(enqueue_research_pipeline(session_id, molecule))
        
        return ResearchStartResponse(
            session_id=str(session_id),
            status="running",
            canonical=canonical_name,
            estimated_duration_seconds=180,
            from_cache=False
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stream/{session_id}")
async def stream_progress(session_id: str):
    """Server-Sent Events endpoint for real-time progress updates."""
    
    async def event_generator():
        queue = sse_manager.add_listener(session_id)
        try:
            # Send initial connection event
            yield f"data: {json.dumps({'event': 'connected', 'session_id': session_id})}\n\n"
            
            while True:
                try:
                    # Wait for events with timeout to send keepalive
                    event = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"data: {json.dumps(event)}\n\n"
                    
                    # Close stream after synthesis_complete
                    if event.get("event") == "synthesis_complete":
                        break
                        
                except asyncio.TimeoutError:
                    # Send keepalive comment to prevent connection timeout
                    yield ": keepalive\n\n"
                    
        except asyncio.CancelledError:
            pass
        finally:
            sse_manager.remove_listener(session_id, queue)
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable nginx buffering
        }
    )
