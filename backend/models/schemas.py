from pydantic import BaseModel, Field
from typing import List, Optional

class RepurposingOpportunity(BaseModel):
    target_indication: str
    rationale: str
    clinical_precedent: str
    patent_barrier: str
    opportunity_score: float

class FinalReportSchema(BaseModel):
    executive_summary: str
    mechanism_of_action: str
    opportunities: List[RepurposingOpportunity]
    data_gaps: List[str]

class MoleculeIdentity(BaseModel):
    canonical_name: str
    aliases: List[str]
    description: str

class AgentOutputSchema(BaseModel):
    summary: str
    key_findings: List[str]
    confidence: float
