import os
import uuid
from typing import Dict, Any, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize Supabase client
_supabase: Optional[Client] = None

def get_supabase() -> Client:
    global _supabase
    if _supabase is None:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        _supabase = create_client(url, key)
    return _supabase

async def create_session(molecule: str) -> str:
    """Create a new research session in Supabase"""
    session_id = str(uuid.uuid4())
    sb = get_supabase()
    
    try:
        sb.table("sessions").insert({
            "id": session_id,
            "molecule": molecule,
            "status": "running",
            "created_at": "now()"
        }).execute()
    except Exception as e:
        print(f"Supabase insert failed: {e}. Continuing with session_id anyway.")
    
    return session_id

async def update_session_status(session_id: str, status: str):
    """Update session status"""
    sb = get_supabase()
    try:
        sb.table("sessions").update({"status": status}).eq("id", session_id).execute()
        print(f"Session {session_id} updated to {status}")
    except Exception as e:
        print(f"Supabase update failed: {e}")

async def save_report(session_id: str, report_data: Dict[str, Any]):
    """Save final report to Supabase"""
    sb = get_supabase()
    try:
        # Map FinalReportSchema fields to Supabase schema
        sb.table("reports").insert({
            "session_id": session_id,
            "executive_summary": report_data.get("executive_summary", ""),
            "opportunity_matrix": report_data.get("opportunities", []),
            "data_gaps": report_data.get("data_gaps", []),
            "content_md": report_data.get("mechanism_of_action", ""),  # Store MOA in content_md for now
            "created_at": "now()"
        }).execute()
        print(f"Report saved to Supabase for session {session_id}")
    except Exception as e:
        print(f"Supabase report save failed: {e}")

async def get_report(session_id: str) -> Dict[str, Any]:
    """Fetch report from Supabase"""
    sb = get_supabase()
    try:
        result = sb.table("reports").select("*").eq("session_id", session_id).execute()
        if result.data and len(result.data) > 0:
            row = result.data[0]
            # Reconstruct FinalReportSchema format
            return {
                "executive_summary": row.get("executive_summary", ""),
                "mechanism_of_action": row.get("content_md", ""),
                "opportunities": row.get("opportunity_matrix", []),
                "data_gaps": row.get("data_gaps", [])
            }
    except Exception as e:
        print(f"Supabase report fetch failed: {e}")
    return {}
