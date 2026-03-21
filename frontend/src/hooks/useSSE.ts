import { useState, useEffect } from 'react';

// API base URL configuration
const API_BASE_URL = 
  process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && window.location.hostname !== 'localhost' 
    ? 'https://your-backend-url.com' // Replace with your deployed backend URL
    : 'http://localhost:8000');

// Type describing the status payloads flowing from the backend
export interface AgentProgressEvent {
  event?: string;
  domain: string;
  status: 'started' | 'completed' | 'failed';
  message: string;
  timestamp?: string;
}

export function useSSE(sessionId: string | null, onComplete?: () => void) {
  const [events, setEvents] = useState<AgentProgressEvent[]>([]);
  const [isDone, setIsDone] = useState(false);

  useEffect(() => {
    if (!sessionId) return;

    // Connect to FastAPI SSE endpoint
    const evtSource = new EventSource(`${API_BASE_URL}/api/research/stream/${sessionId}`);

    evtSource.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        
        // Check for synthesis complete event
        if (data.event === 'synthesis_complete' || data.status === 'synthesis_complete') {
          setIsDone(true);
          evtSource.close();
          // Call the completion callback
          if (onComplete) {
            onComplete();
          }
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
  }, [sessionId, onComplete]);

  return { events, isDone };
}
