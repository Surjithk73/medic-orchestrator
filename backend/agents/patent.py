import os
import httpx
import asyncio
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
        print("EPO credentials not found in environment")
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
            token = r.json().get("access_token")
            print(f"EPO token obtained successfully")
            return token
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
        epo_success = False

        # 1. EPO OPS (requires EPO_CLIENT_ID + EPO_CLIENT_SECRET in .env)
        try:
            token = await _get_epo_token()
            if token:
                print(f"[{self.session_id}] Searching EPO for: {canon}")
                async with httpx.AsyncClient(timeout=30) as client:
                    # Try multiple search strategies
                    search_queries = [
                        f'ti="{canon}"',  # Title search
                        f'ta="{canon}"',  # Title and abstract
                        canon  # Simple keyword search
                    ]
                    
                    for query in search_queries:
                        try:
                            print(f"[{self.session_id}] EPO query: {query}")
                            r = await client.get(
                                EPO_SEARCH_URL,
                                params={"q": query},
                                headers={
                                    "Authorization": f"Bearer {token}",
                                    "Accept": "application/json"
                                }
                            )
                            print(f"[{self.session_id}] EPO response status: {r.status_code}")
                            
                            if r.status_code == 200:
                                data = r.json()
                                print(f"[{self.session_id}] EPO response keys: {data.keys()}")
                                
                                # Navigate the nested structure
                                world_data = data.get("ops:world-patent-data", {})
                                biblio_search = world_data.get("ops:biblio-search", {})
                                
                                # Check total results
                                total_results = biblio_search.get("@total-result-count", "0")
                                print(f"[{self.session_id}] EPO total results: {total_results}")
                                
                                if int(total_results) > 0:
                                    search_result = biblio_search.get("ops:search-result", {})
                                    results = search_result.get("exchange-documents", [])
                                    
                                    if isinstance(results, dict):
                                        results = [results]
                                    
                                    num_patents = len(results)
                                    print(f"[{self.session_id}] EPO: {num_patents} patents found")
                                    
                                    for doc in results[:10]:
                                        try:
                                            biblio = doc.get("exchange-document", doc)
                                            biblio_data = biblio.get("bibliographic-data", {})
                                            pub_ref = biblio_data.get("publication-reference", {})
                                            doc_id = pub_ref.get("document-id", [])
                                            
                                            # Handle both list and dict formats
                                            if isinstance(doc_id, list):
                                                doc_id = doc_id[0] if doc_id else {}
                                            
                                            doc_num = doc_id.get("doc-number", {})
                                            country = doc_id.get("country", {})
                                            
                                            # Extract values (can be nested dicts with "$" key)
                                            num_val = doc_num.get("$", doc_num) if isinstance(doc_num, dict) else doc_num
                                            country_val = country.get("$", country) if isinstance(country, dict) else country
                                            
                                            # Get title if available
                                            invention_title = biblio_data.get("invention-title", [])
                                            if isinstance(invention_title, list):
                                                invention_title = invention_title[0] if invention_title else {}
                                            title_text = invention_title.get("$", "No title") if isinstance(invention_title, dict) else str(invention_title)
                                            
                                            patent_context += f"Patent: {num_val} | Country: {country_val} | Title: {title_text[:100]}\n"

                                            await self.add_citation(
                                                url=f"https://worldwide.espacenet.com/patent/search?q={num_val}",
                                                title=f"Patent {num_val} ({country_val})"
                                            )
                                        except Exception as doc_err:
                                            print(f"[{self.session_id}] Error parsing patent doc: {doc_err}")
                                            continue
                                    
                                    epo_success = True
                                    break  # Found results, stop trying other queries
                            else:
                                print(f"[{self.session_id}] EPO search returned {r.status_code}: {r.text[:500]}")
                        except Exception as query_err:
                            print(f"[{self.session_id}] EPO query '{query}' failed: {query_err}")
                            continue
            else:
                print(f"[{self.session_id}] EPO credentials not set — skipping EPO search")
        except Exception as e:
            print(f"[{self.session_id}] EPO API error: {e}")
            import traceback
            traceback.print_exc()

        # 2. Open Targets GraphQL — known drug indications (free, no auth)
        try:
            chembl_id = entity.get("chembl_id", "")
            if chembl_id:
                print(f"[{self.session_id}] Querying Open Targets for ChEMBL ID: {chembl_id}")
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
                    print(f"[{self.session_id}] Open Targets: {len(indications)} indications found")
                    for ind in indications[:10]:
                        disease = ind.get("disease", {}).get("name", "N/A")
                        phase = ind.get("maxPhaseForIndication", "N/A")
                        patent_context += f"Known indication: {disease} (max phase: {phase})\n"
                else:
                    print(f"[{self.session_id}] Open Targets: No drug data found")
        except Exception as e:
            print(f"[{self.session_id}] Open Targets error: {e}")

        # If no patents found, add a note
        if num_patents == 0:
            patent_context += f"\nNote: No patents directly found via EPO search for '{canon}'. This could indicate:\n"
            patent_context += "- The molecule is off-patent (composition-of-matter patents expired)\n"
            patent_context += "- Patents exist under different names/synonyms\n"
            patent_context += "- Method-of-use patents may exist for specific indications\n"

        prompt = (
            f"Analyze the patent landscape and freedom-to-operate for {canon}.\n\n"
            f"Available patent/indication data ({num_patents} patents found):\n"
            f"{patent_context if patent_context else 'No direct patent data retrieved — use general knowledge.'}\n\n"
            f"Assess: composition-of-matter patent status, method-of-use patents per indication, "
            f"estimated expiry windows, and FTO for novel repurposing indications. "
            f"If no patents were found, explain what this means for freedom-to-operate."
        )

        output = await self.extract_knowledge(prompt)
        await context_manager.save_agent_summary(self.session_id, "patent", output.summary)
        await self.log_trace("complete", {"num_patents": num_patents, "confidence": output.confidence})
        await self.emit_sse("agent_completed", {"status": "completed", "message": f"Analyzed {num_patents} patents"})
        return output.model_dump()
