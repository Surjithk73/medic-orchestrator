import os
from typing import Dict, Any
import httpx
from dotenv import load_dotenv

load_dotenv()

class ContextManagerObj:
    """Redis-backed context manager using Upstash REST API"""
    
    def __init__(self):
        self._url = os.environ.get("UPSTASH_REDIS_REST_URL")
        self._token = os.environ.get("UPSTASH_REDIS_REST_TOKEN")
        if not self._url or not self._token:
            raise ValueError("UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN must be set")
        self._headers = {"Authorization": f"Bearer {self._token}"}
        
    async def _redis_command(self, *args):
        """Execute Redis command via REST API"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self._url,
                json=args,
                headers=self._headers
            )
            data = response.json()
            return data.get("result")
        
    async def set_session_entity(self, session_id: str, identity: dict):
        """Store molecule identity for this session"""
        key = f"session:{session_id}:entity"
        await self._redis_command("SET", key, str(identity), "EX", 86400)
        
    async def get_session_entity(self, session_id: str) -> dict:
        """Retrieve molecule identity for this session"""
        key = f"session:{session_id}:entity"
        data = await self._redis_command("GET", key)
        if data:
            import ast
            return ast.literal_eval(data)
        return {}
        
    async def save_agent_summary(self, session_id: str, domain: str, md_text: str):
        """Save compressed domain summary for synthesis"""
        key = f"session:{session_id}:summary:{domain}"
        await self._redis_command("SET", key, md_text, "EX", 86400)
        
    async def get_all_summaries(self, session_id: str) -> dict:
        """Retrieve all 4 domain summaries"""
        res = {}
        for d in ["clinical", "patent", "market", "regulatory"]:
            key = f"session:{session_id}:summary:{d}"
            val = await self._redis_command("GET", key)
            res[d] = val if val else f"No data for {d}."
        return res

context_manager = ContextManagerObj()
