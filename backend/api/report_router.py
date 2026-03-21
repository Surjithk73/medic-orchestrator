from fastapi import APIRouter, HTTPException
import os
import json

router = APIRouter()

@router.get("/{session_id}")
async def fetch_report(session_id: str):
    path = f"tmp_reports/{session_id}.json"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Report not generated yet")
    
    with open(path, "r") as f:
        report_data = json.load(f)
    
    # Fetch citations from Redis
    from backend.memory.citation_ledger import citation_ledger
    try:
        citations = await citation_ledger.get_all(session_id)
        report_data["citations"] = citations
    except Exception as e:
        print(f"Failed to fetch citations: {e}")
        report_data["citations"] = []
    
    # Fetch trace events from SSE manager history
    from backend.memory.sse_manager import sse_manager
    try:
        trace_events = sse_manager.get_session_history(session_id)
        report_data["trace_events"] = trace_events
    except Exception as e:
        print(f"Failed to fetch trace events: {e}")
        report_data["trace_events"] = []
    
    return report_data

@router.get("/{session_id}/citations")
async def fetch_citations(session_id: str):
    """Fetch all citations for a session from Redis citation ledger"""
    from backend.memory.citation_ledger import citation_ledger
    try:
        citations = await citation_ledger.get_all(session_id)
        return {
            "session_id": session_id,
            "count": len(citations),
            "citations": citations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cache/{molecule}")
async def check_cache(molecule: str):
    """Check if a cached report exists for a molecule"""
    from backend.memory.report_cache import report_cache
    try:
        exists = await report_cache.exists(molecule)
        ttl = await report_cache.get_ttl(molecule) if exists else None
        return {
            "molecule": molecule,
            "cached": exists,
            "ttl_seconds": ttl,
            "ttl_hours": round(ttl / 3600, 1) if ttl else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cache/{molecule}")
async def invalidate_cache(molecule: str):
    """Manually invalidate a cached report"""
    from backend.memory.report_cache import report_cache
    try:
        await report_cache.invalidate(molecule)
        return {"molecule": molecule, "status": "invalidated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
