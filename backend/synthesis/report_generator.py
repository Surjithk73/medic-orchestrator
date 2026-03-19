from backend.models.schemas import FinalReportSchema
from backend.db.supabase_client import save_report
from backend.memory.report_cache import report_cache
from backend.memory.context_manager import context_manager
import os
import json

class ReportGenerator:
    """Report generator that saves to both Supabase and local cache"""
    async def finalize_and_save(self, session_id: str, report_data: FinalReportSchema):
        print(f"[{session_id}] Finalizing report...")
        
        report_dict = report_data.model_dump()
        
        # Save to Supabase
        await save_report(session_id, report_dict)
        
        # Also save to local cache for frontend polling (temporary until SSE is wired)
        os.makedirs("tmp_reports", exist_ok=True)
        with open(f"tmp_reports/{session_id}.json", "w") as f:
            json.dump(report_dict, f, indent=2)
        
        # Cache the report in Redis for future requests
        entity = await context_manager.get_session_entity(session_id)
        canonical_name = entity.get("canonical_name", "")
        if canonical_name:
            await report_cache.set(canonical_name, report_dict)
        
        print(f"[{session_id}] Report saved to Supabase and tmp_reports/{session_id}.json")

report_generator = ReportGenerator()
