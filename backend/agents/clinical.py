from backend.agents.base import BaseAgent
from backend.retrieval.chunker import chunk_by_semantic_boundary
from backend.retrieval.embedder import embed_chunks
from backend.db.qdrant_client import upsert_chunks, hybrid_search
from backend.memory.context_manager import context_manager
import requests as req_lib

# ClinicalTrials.gov blocks httpx via TLS fingerprinting — use requests instead
CT_BASE = "https://clinicaltrials.gov/api/v2"
CT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9"
}


class ClinicalAgent(BaseAgent):
    domain = "clinical"

    async def execute(self) -> dict:
        print(f"[{self.session_id}] ClinicalAgent fetching clinical trials...")
        await self.emit_sse("agent_started", {"status": "started", "message": "Fetching clinical trials..."})
        
        entity = await context_manager.get_session_entity(self.session_id)
        canon = entity.get("canonical_name", "Unknown")

        all_text = ""
        num_studies = 0

        try:
            # query.intr searches the Intervention/Treatment search area (drug name, synonyms)
            # This is more targeted than query.term for drug repurposing use cases
            response = req_lib.get(
                f"{CT_BASE}/studies",
                params={
                    "query.intr": canon,
                    "pageSize": 50,
                    "format": "json"
                },
                headers=CT_HEADERS,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            studies = data.get("studies", [])
            num_studies = len(studies)
            print(f"[{self.session_id}] ClinicalTrials: {num_studies} studies found for {canon}")

            for study in studies[:20]:
                protocol = study.get("protocolSection", {})
                ident = protocol.get("identificationModule", {})
                status_mod = protocol.get("statusModule", {})
                design = protocol.get("designModule", {})
                conditions = protocol.get("conditionsModule", {}).get("conditions", [])
                desc = protocol.get("descriptionModule", {})
                interv_mod = protocol.get("armsInterventionsModule", {})
                interventions = [iv.get("name", "") for iv in interv_mod.get("interventions", [])[:5]]

                nct_id = ident.get("nctId", "N/A")
                study_text = (
                    f"NCT ID: {nct_id}\n"
                    f"Title: {ident.get('briefTitle', 'N/A')}\n"
                    f"Status: {status_mod.get('overallStatus', 'N/A')}\n"
                    f"Phase: {', '.join(design.get('phases', ['N/A']))}\n"
                    f"Conditions: {', '.join(conditions[:5])}\n"
                    f"Interventions: {', '.join(interventions)}\n"
                    f"Summary: {desc.get('briefSummary', '')[:300]}\n"
                )
                all_text += study_text + "\n\n"

                # Record citation
                await self.add_citation(
                    url=f"https://clinicaltrials.gov/study/{nct_id}",
                    title=ident.get("briefTitle", nct_id)
                )

            # Chunk → embed → upsert → retrieve
            chunks = chunk_by_semantic_boundary(all_text, max_tokens=400)
            if chunks:
                chunk_texts = [c["text"] for c in chunks]
                vectors = await embed_chunks(chunk_texts)

                qdrant_chunks = [
                    {
                        "id": abs(hash(f"{self.session_id}_clinical_{i}")) % (2**63),
                        "text": c["text"],
                        "source_url": "https://clinicaltrials.gov",
                        "section": c["section"],
                        "metadata": {"session_id": self.session_id, "domain": "clinical"}
                    }
                    for i, c in enumerate(chunks)
                ]
                await upsert_chunks("drug_clinical", qdrant_chunks, vectors)

                query_vec = await embed_chunks([f"clinical trials repurposing {canon}"])
                search_results = await hybrid_search("drug_clinical", query_vec[0], canon, limit=10)
                context = "\n\n".join([r["text"] for r in search_results])
            else:
                context = all_text[:3000]

        except Exception as e:
            print(f"[{self.session_id}] ClinicalTrials API error: {e}")
            context = f"API unavailable. Proceeding with general knowledge for {canon}."

        prompt = (
            f"Summarize clinical trial activity for {canon}.\n\n"
            f"Data from ClinicalTrials.gov ({num_studies} studies found):\n{context}\n\n"
            f"Extract key findings: trial phases, indications being studied, "
            f"completion status, and any repurposing signals (Phase 2+ evidence for non-approved indications)."
        )

        output = await self.extract_knowledge(prompt)
        await context_manager.save_agent_summary(self.session_id, "clinical", output.summary)
        await self.log_trace("complete", {"num_studies": num_studies, "confidence": output.confidence})
        await self.emit_sse("agent_completed", {"status": "completed", "message": f"Analyzed {num_studies} clinical trials"})
        return output.model_dump()
