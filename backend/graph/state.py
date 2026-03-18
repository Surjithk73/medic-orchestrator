from typing_extensions import TypedDict
from typing import List, Dict, Any

class ResearchState(TypedDict):
    session_id: str
    molecule_name: str
    pending_tasks: List[str]
    completed_tasks: List[str]
    failed_tasks: List[str]
    agent_outputs: Dict[str, Any]
    all_domains_complete: bool
    synthesis_ready: bool
