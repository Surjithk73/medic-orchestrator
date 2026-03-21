/**
 * API configuration
 * Uses environment variable in production, localhost in development
 */
const rawUrl = process.env.NEXT_PUBLIC_API_URL || 
  (typeof window !== 'undefined' && window.location.hostname !== 'localhost' 
    ? 'https://medic-orchestrator-production.up.railway.app'
    : 'http://localhost:8080');

// Strip trailing slash to prevent double-slash in API paths
export const API_BASE_URL = rawUrl.replace(/\/$/, '');

export const SITE_URL = 'https://medorch.vercel.app';
