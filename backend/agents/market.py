from backend.agents.base import BaseAgent
from backend.retrieval.api_client import api_client
from backend.memory.context_manager import context_manager
import os

class MarketAgent(BaseAgent):
    domain = "market"

    async def execute(self) -> dict:
        print(f"[{self.session_id}] MarketAgent analyzing market landscape...")
        await self.emit_sse("agent_started", {"status": "started", "message": "Analyzing market landscape..."})
        
        entity = await context_manager.get_session_entity(self.session_id)
        canon = entity.get("canonical_name", "Unknown")
        
        market_context = ""
        
        try:
            # OpenFDA drug labels
            api_key = os.environ.get("OPENFDA_API_KEY", "")
            response = await api_client.get(
                "https://api.fda.gov/drug/label.json",
                params={
                    "search": f'openfda.generic_name:"{canon}"',
                    "limit": 5
                }
            )
            data = response.json()
            results = data.get("results", [])
            
            for label in results:
                openfda = label.get("openfda", {})
                brand_names = openfda.get("brand_name", ["N/A"])
                indications = label.get("indications_and_usage", ["N/A"])
                
                market_context += f"""
Brand: {', '.join(brand_names[:3])}
Indications: {indications[0][:300] if indications else 'N/A'}...
"""
                
        except Exception as e:
            print(f"[{self.session_id}] OpenFDA API error: {e}")
            market_context = f"Limited market data available. Error: {e}"
        
        prompt = f"""Analyze market landscape for {canon}.

OpenFDA data:
{market_context}

Assess: approved indications, competing products, market saturation, and unmet needs."""
        
        output = await self.extract_knowledge(prompt)
        await context_manager.save_agent_summary(self.session_id, "market", output.summary)
        await self.log_trace("complete", {"confidence": output.confidence})
        await self.emit_sse("agent_completed", {"status": "completed", "message": "Market analysis complete"})
        return output.model_dump()
