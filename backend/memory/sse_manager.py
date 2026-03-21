import asyncio
from typing import Dict, Set, List
from collections import defaultdict


class SSEManager:
    """
    Manages Server-Sent Events (SSE) connections for real-time progress updates.
    Each session can have multiple listeners (browser tabs).
    """

    def __init__(self):
        # session_id -> set of asyncio.Queue objects (one per connected client)
        self._listeners: Dict[str, Set[asyncio.Queue]] = defaultdict(set)
        # session_id -> list of events (for trace history)
        self._history: Dict[str, List[dict]] = defaultdict(list)

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
        """Broadcast an event to all listeners for a session and store in history."""
        # Store in history
        import datetime
        event_with_timestamp = {**event, "timestamp": datetime.datetime.utcnow().isoformat()}
        self._history[session_id].append(event_with_timestamp)
        
        if session_id not in self._listeners:
            return

        # Send to all connected clients
        for queue in list(self._listeners[session_id]):
            try:
                await asyncio.wait_for(queue.put(event_with_timestamp), timeout=1.0)
            except asyncio.TimeoutError:
                # Queue full or slow client — skip
                pass
            except Exception as e:
                print(f"SSE emit error: {e}")

    def get_listener_count(self, session_id: str) -> int:
        """Return number of active listeners for a session."""
        return len(self._listeners.get(session_id, set()))
    
    def get_session_history(self, session_id: str) -> List[dict]:
        """Return all events for a session."""
        return self._history.get(session_id, [])
    
    def clear_history(self, session_id: str):
        """Clear event history for a session."""
        if session_id in self._history:
            del self._history[session_id]


sse_manager = SSEManager()
