import json
from typing import List, Dict, Any
from backend.memory.context_manager import context_manager


class CitationLedger:
    """
    Lightweight citation ledger backed by Upstash Redis.
    Each session accumulates a list of citation records keyed by session_id.
    """

    def _key(self, session_id: str) -> str:
        return f"session:{session_id}:citations"

    async def add(self, session_id: str, domain: str, url: str, title: str, extra: Dict[str, Any] = None):
        """Append a citation record to the session ledger."""
        record = {"domain": domain, "url": url, "title": title}
        if extra:
            record.update(extra)
        try:
            key = self._key(session_id)
            # RPUSH appends to a Redis list
            await context_manager._redis_command("RPUSH", key, json.dumps(record))
            # Refresh TTL
            await context_manager._redis_command("EXPIRE", key, 86400)
        except Exception as e:
            print(f"CitationLedger.add failed: {e}")

    async def get_all(self, session_id: str) -> List[Dict[str, Any]]:
        """Return all citations for a session."""
        try:
            key = self._key(session_id)
            raw_list = await context_manager._redis_command("LRANGE", key, 0, -1)
            if not raw_list:
                return []
            return [json.loads(item) for item in raw_list]
        except Exception as e:
            print(f"CitationLedger.get_all failed: {e}")
            return []

    async def count(self, session_id: str) -> int:
        """Return citation count for a session."""
        try:
            key = self._key(session_id)
            result = await context_manager._redis_command("LLEN", key)
            return int(result) if result else 0
        except Exception:
            return 0


citation_ledger = CitationLedger()
