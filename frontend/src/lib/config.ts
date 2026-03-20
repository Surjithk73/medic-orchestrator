/**
 * API configuration
 * Uses environment variable in production, localhost in development
 */
export const API_BASE_URL = 
  process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && window.location.hostname !== 'localhost' 
    ? 'https://your-backend-url.com' // Replace with your deployed backend URL
    : 'http://localhost:8000');
