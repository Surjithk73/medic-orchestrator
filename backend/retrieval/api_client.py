import asyncio
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class APIClient:
    """Async HTTP client for fetching external data with built-in retries."""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.default_headers = {
            "User-Agent": "MedicOrchestrator/1.0 (Research; +https://github.com/medic-orchestrator)",
            "Accept": "application/json"
        }
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException))
    )
    async def get(self, url: str, params: dict = None, headers: dict = None) -> httpx.Response:
        # Merge default headers with provided headers
        merged_headers = {**self.default_headers, **(headers or {})}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params, headers=merged_headers)
            response.raise_for_status()
            return response
            
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException))
    )
    async def post(self, url: str, json: dict = None, data: dict = None, headers: dict = None) -> httpx.Response:
        # Merge default headers with provided headers
        merged_headers = {**self.default_headers, **(headers or {})}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=json, data=data, headers=merged_headers)
            response.raise_for_status()
            return response

# Global instance for easy import
api_client = APIClient()
