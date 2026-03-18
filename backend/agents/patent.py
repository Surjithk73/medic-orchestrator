import os
import httpx
from backend.agents.base import BaseAgent
from backend.retrieval.api_client import api_client
from backend.memory.context_manager import context_manager

EPO_TOKEN_URL = "https://ops.epo.org/3.2/auth/accesstoken"
EPO_SEARCH_URL = "https://ops.epo.org/3.2/rest-services/published-data/search"


async def _get_epo_token() -> str | None:
    """Get EPO OPS OAuth2 access token."""
    client_id = os.environ.get("EPO_CLIENT_ID", "")
    client_secret = os.environ.get("EPO_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        return None
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            r = await client.post(
                EPO_TOKEN_URL,
                data={"grant_type": "client_credentials"},
                auth=(client_id, client_secret),
                headers={"Accept": "application/json"}
            )
            r.raise_for_status()
            return r.json().get("access_token")
    except Exception as e:
        print(f"EPO token error: {e}")
        return None


class PatentAgent(BaseAgent):
    domain = "patent"

    async def execute(self) -> dict:
        print(f"[{self.session_id}] PatentAgent fetching patent data...")
        await self.emit_sse("agent_started", {"status": "started", "message": "Analyzing patent landscape..."})
        
        entity = await context_manager.get_session_entity(self.session_id)
        canon = entity.get("canonical_name", "Unknown")

        patent_context = ""
        num_patents = 0

        # 1. EPO OPS (requires EPO_CLIENT_ID + EPO_CLIENT_SECRET in .env)
        try:
            token = await _get_epo_token()
            if token:
                async with httpx.AsyncClient(timeout=30) as client:
                    r = await client.get(
                        EPO_SEARCH_URL,
                        params={"q": f'ti="{canon}" OR ab="{canon}"', "Range": "1-10"},
                        headers={
                            "Authorization": f"Bearer {token}",
                            "Accept": "application/json",
                            "X-OPS-Range": "1-10"
                        }
                    )
                    if r.status_code == 200:
                        data = r.json()
                        results = (
                            data.get("ops:world-patent-data", {})
                                .get("ops:biblio-search", {})
                                .get("ops:search-result", {})
                                .get("exchange-documents", [])
                        )
                        if isinstance(results, dict):
                            results = [results]
                        num_patents = len(results)
                        for doc in results[:10]:
                            biblio = doc.get("exchange-document", doc)
                            pub_ref = (
                                biblio.get("bibliographic-data", {})
                                      .get("publication-reference", {})
                            )
                            doc_id = pub_ref.get("document-id", {})
                            doc_num = doc_id.get("doc-number", {})
                            country = doc_id.get("country", {})
                            # doc-number and country can be dicts with "$" key or plain strings
                            num_val = doc_num.get("$", doc_num) if isinstance(doc_num, dict) else doc_num
                            country_val = country.get("$", country) if isinstance(country, dict) else country
                            patent_context += f"Patent: {num_val} | Country: {country_val}\n"

                            await self.add_citation(
                                url=f"https://ops.epo.org/3.2/rest-services/published-data/publication/epodoc/{num_val}",
                                title=f"Patent {num_val} ({country_val})"
                            )
                        print(f"[{self.session_id}] EPO: {num_patents} patents found")
                    else:
                        print(f"[{self.session_id}] EPO search returned {r.status_code}: {r.text[:200]}")
            else:
                print(f"[{self.session_id}] EPO credentials not set — skipping EPO search")
        except Exception as e:
            print(f"[{self.session_id}] EPO API error: {e}")

        # 2. Open Targets GraphQL — known drug indications (free, no auth)
        try:
            chembl_id = entity.get("chembl_id", "")
            if chembl_id:
                query = """
                query($chemblId: String!) {
                  drug(chemblId: $chemblId) {
                    name
                    indications { rows { disease { name } maxPhaseForIndication } }
                  }
                }
                """
                r = await api_client.post(
                    "https://api.platform.opentargets.org/api/v4/graphql",
                    json={"query": query, "variables": {"chemblId": chembl_id}}
                )
                ot_data = r.json().get("data", {}).get("drug", {})
                if ot_data:
                    indications = ot_data.get("indications", {}).get("rows", [])
                    for ind in indications[:10]:
                        disease = ind.get("disease", {}).get("name", "N/A")
                        phase = ind.get("maxPhaseForIndication", "N/A")
                        patent_context += f"Known indication: {disease} (max phase: {phase})\n"
        except Exception as e:
            print(f"[{self.session_id}] Open Targets error: {e}")

        prompt = (
            f"Analyze the patent landscape and freedom-to-operate for {canon}.\n\n"
            f"Available patent/indication data:\n"
            f"{patent_context if patent_context else 'No direct patent data retrieved — use general knowledge.'}\n\n"
            f"Assess: composition-of-matter patent status, method-of-use patents per indication, "
            f"estimated expiry windows, and FTO for novel repurposing indications."
        )

        output = await self.extract_knowledge(prompt)
        await context_manager.save_agent_summary(self.session_id, "patent", output.summary)
        await self.log_trace("complete", {"num_patents": num_patents, "confidence": output.confidence})
        await self.emit_sse("agent_completed", {"status": "completed", "message": f"Analyzed {num_patents} patents"})
        return output.model_dump()
