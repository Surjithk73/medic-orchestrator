from backend.agents.base import BaseAgent
from backend.retrieval.api_client import api_client
from backend.memory.context_manager import context_manager
import os

class RegulatoryAgent(BaseAgent):
    domain = "regulatory"

    async def execute(self) -> dict:
        print(f"[{self.session_id}] RegulatoryAgent checking regulatory status...")
        await self.emit_sse("agent_started", {"status": "started", "message": "Checking regulatory status..."})
        
        entity = await context_manager.get_session_entity(self.session_id)
        canon = entity.get("canonical_name", "Unknown")
        
        regulatory_context = ""
        
        # 1. FDA DailyMed
        try:
            response = await api_client.get(
                "https://dailymed.nlm.nih.gov/dailymed/services/v2/spls.json",
                params={"drug_name": canon, "pagesize": 5}
            )
            data = response.json()
            spls = data.get("data", [])
            
            if spls:
                setid = spls[0].get("setid")
                title = spls[0].get("title", "N/A")
                regulatory_context += f"FDA Label: {title}\nSPL Set ID: {setid}\n\n"
                try:
                    hist = await api_client.get(
                        f"https://dailymed.nlm.nih.gov/dailymed/services/v2/spls/{setid}/history.json"
                    )
                    history = hist.json().get("data", [])
                    if history:
                        regulatory_context += f"Label versions: {len(history)} (earliest: {history[-1].get('published', 'N/A')})\n"
                except Exception:
                    pass
            else:
                regulatory_context += f"No FDA DailyMed label found for {canon}.\n"
        except Exception as e:
            print(f"[{self.session_id}] FDA DailyMed error: {e}")
            regulatory_context += "FDA DailyMed unavailable.\n"

        # 2. OpenFDA adverse events
        try:
            api_key = os.environ.get("OPENFDA_API_KEY", "")
            params = {
                "search": f'patient.drug.medicinalproduct:"{canon}"',
                "count": "seriousnessother",
                "limit": 5
            }
            if api_key:
                params["api_key"] = api_key
            ae_response = await api_client.get("https://api.fda.gov/drug/event.json", params=params)
            ae_data = ae_response.json()
            results = ae_data.get("results", [])
            if results:
                top_aes = [f"{r.get('term', 'N/A')} (n={r.get('count', 0)})" for r in results[:5]]
                regulatory_context += f"\nTop adverse event signals: {', '.join(top_aes)}\n"
        except Exception as e:
            print(f"[{self.session_id}] OpenFDA adverse events error: {e}")

        prompt = (
            f"Analyze the regulatory profile for {canon}.\n\n"
            f"Regulatory data:\n{regulatory_context}\n\n"
            f"Assess: approval status, black box warnings, orphan designations, "
            f"special designations (fast-track, breakthrough), and key safety signals."
        )
        
        output = await self.extract_knowledge(prompt)
        await context_manager.save_agent_summary(self.session_id, "regulatory", output.summary)
        await self.log_trace("complete", {"confidence": output.confidence})
        await self.emit_sse("agent_completed", {"status": "completed", "message": "Regulatory analysis complete"})
        return output.model_dump()
