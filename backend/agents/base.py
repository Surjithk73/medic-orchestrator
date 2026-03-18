from backend.models.schemas import AgentOutputSchema
from backend.models.llm_router import get_router
from backend.memory.context_manager import context_manager


class BaseAgent:
    domain: str = "base"

    def __init__(self, session_id: str):
        self.session_id = session_id

    async def execute(self) -> dict:
        raise NotImplementedError

    async def extract_knowledge(self, prompt: str) -> AgentOutputSchema:
        return await get_router().invoke_extraction(prompt, AgentOutputSchema)

    async def log_trace(self, step: str, data: dict):
        """Log an agent trace step (stored in Redis for now)."""
        try:
            key = f"session:{self.session_id}:trace:{self.domain}:{step}"
            import json
            await context_manager._redis_command("SET", key, json.dumps(data), "EX", 86400)
        except Exception as e:
            print(f"[{self.session_id}] log_trace failed: {e}")

    async def add_citation(self, url: str, title: str, domain: str = None):
        """Record a citation in the citation ledger."""
        from backend.memory.citation_ledger import citation_ledger
        await citation_ledger.add(
            session_id=self.session_id,
            domain=domain or self.domain,
            url=url,
            title=title
        )

    async def emit_sse(self, event: str, data: dict):
        """Emit an SSE event to all connected clients."""
        from backend.memory.sse_manager import sse_manager
        await sse_manager.emit(self.session_id, {
            "event": event,
            "domain": self.domain,
            **data
        })
