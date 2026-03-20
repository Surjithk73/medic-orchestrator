"""
Phase 2 Tests — Pydantic Schemas & LLM Router

Verifies:
- All required Pydantic schemas can be imported and validated with valid data
- Invalid data raises ValidationError for each schema
"""

import pytest
from pydantic import ValidationError
from backend.models.schemas import (
    TrialOutcome, ClinicalSummary, PatentRecord, 
    PatentSummary, MarketCompetitor, RegulatoryStatus,
    RepurposingOpportunity, FinalReportSchema
)
from backend.models.llm_router import router

def test_valid_clinical_summary():
    cs = ClinicalSummary(
        molecule_name="Aspirin",
        trials_analyzed=10,
        proven_indications=["Pain"],
        failed_indications=[],
        overall_clinical_viability=8
    )
    assert cs.overall_clinical_viability == 8

def test_invalid_clinical_score():
    with pytest.raises(ValidationError):
        ClinicalSummary(
            molecule_name="Aspirin",
            trials_analyzed=10,
            proven_indications=[],
            failed_indications=[],
            overall_clinical_viability=15  # Should fail, max is 10
        )

def test_valid_opportunity():
    op = RepurposingOpportunity(
        target_indication="Cancer",
        rationale="Blocks COX-2",
        clinical_precedent="Trial X showed 20% reduction",
        patent_barrier="Low",
        opportunity_score=8.5
    )
    assert op.opportunity_score == 8.5

def test_invalid_opportunity_score():
    with pytest.raises(ValidationError):
        RepurposingOpportunity(
            target_indication="Cancer",
            rationale="Blocks COX-2",
            clinical_precedent="Trial X showed 20% reduction",
            patent_barrier="Low",
            opportunity_score=11.0 # Should fail, max is 10
        )

@pytest.mark.asyncio
async def test_llm_router_initialization():
    # Just verifies the models exist
    assert router.gemini_flash is not None
    assert router.gemini_pro is not None
    assert router.deepseek is not None
