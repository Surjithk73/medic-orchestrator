import asyncio
from typing import Dict, Set
from collections import defaultdict


class SSEManager:
    """
    Manages Server-Sent Events (SSE) connections for real-time progress updates.
    Each session can have multiple listeners (browser tabs).
    """

    def __init__(self):
        # session_id -> set of asyncio.Queue objects (one per connected client)
        self._listeners: Dict[str, Set[asyncio.Queue]] = defaultdict(set)

    def add_listener(self, session_id: str) -> asyncio.Queue:
        """Register a new SSE client for a session."""
        queue = asyncio.Queue(maxsize=100)
        self._listeners[session_id].add(queue)
        return queue

    def remove_listener(self, session_id: str, queue: asyncio.Queue):
        """Unregister an SSE client."""
        if session_id in self._listeners:
            self._listeners[session_id].discard(queue)
            if not self._listeners[session_id]:
                del self._listeners[session_id]

    async def emit(self, session_id: str, event: dict):
        """Broadcast an event to all listeners for a session."""
        if session_id not in self._listeners:
            return

        # Send to all connected clients
        for queue in list(self._listeners[session_id]):
            try:
                await asyncio.wait_for(queue.put(event), timeout=1.0)
            except asyncio.TimeoutError:
                # Queue full or slow client — skip
                pass
            except Exception as e:
                print(f"SSE emit error: {e}")

    def get_listener_count(self, session_id: str) -> int:
        """Return number of active listeners for a session."""
        return len(self._listeners.get(session_id, set()))


sse_manager = SSEManager()
