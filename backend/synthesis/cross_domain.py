from backend.models.schemas import FinalReportSchema
from backend.models.llm_router import get_router
from backend.memory.context_manager import context_manager
from backend.memory.conflict_detector import conflict_detector


class SynthesisEngine:
    async def run_synthesis(self, session_id: str) -> FinalReportSchema:
        print(f"[{session_id}] Synthesis engine starting cross-domain analysis...")
        entity = await context_manager.get_session_entity(session_id)
        canon = entity.get("canonical_name", "Unknown Molecule")

        summaries = await context_manager.get_all_summaries(session_id)

        # Detect cross-domain conflicts before synthesis
        conflicts = conflict_detector.detect(summaries)
        conflict_text = ""
        if conflicts:
            conflict_text = "\n\nDetected cross-domain conflicts (flag these in data_gaps):\n"
            for c in conflicts:
                conflict_text += f"- [{' vs '.join(c['domains'])}] {c['signal']}\n"

        prompt = f"""You are a bio-pharma strategist. Synthesize all domain findings for {canon}.

Clinical summary:
{summaries.get('clinical', 'No data.')}

Patent summary:
{summaries.get('patent', 'No data.')}

Market summary:
{summaries.get('market', 'No data.')}

Regulatory summary:
{summaries.get('regulatory', 'No data.')}
{conflict_text}

Identify repurposing opportunities where:
1. There is clinical evidence (Phase 2+ trials or strong mechanistic rationale)
2. Freedom-to-operate exists (patent expired or method-of-use not covered)
3. An unmet market need exists

Score each opportunity 0.0–1.0 based on combined evidence strength.
Output exactly according to FinalReportSchema.
"""

        return await get_router().invoke_extraction(prompt, FinalReportSchema)


synthesis_engine = SynthesisEngine()
