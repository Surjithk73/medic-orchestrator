import { useState, useEffect } from 'react';

// Type describing the status payloads flowing from the backend
export interface AgentProgressEvent {
  domain: string;
  status: 'started' | 'completed' | 'failed';
  message: string;
}

export function useSSE(sessionId: string | null) {
  const [events, setEvents] = useState<AgentProgressEvent[]>([]);
  const [isDone, setIsDone] = useState(false);

  useEffect(() => {
    if (!sessionId) return;

    // Connect to FastAPI SSE endpoint
    const evtSource = new EventSource(`http://localhost:8000/api/research/stream/${sessionId}`);

    evtSource.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.status === 'synthesis_complete') {
          setIsDone(true);
          evtSource.close();
        } else {
          setEvents((prev) => [...prev, data as AgentProgressEvent]);
        }
      } catch (err) {
        console.error("SSE parse error", err);
      }
    };

    evtSource.onerror = () => {
      console.error("SSE stream error/closed");
      evtSource.close();
    };

    return () => {
      evtSource.close();
    };
  }, [sessionId]);

  return { events, isDone };
}
