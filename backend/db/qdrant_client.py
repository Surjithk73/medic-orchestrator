import os
from typing import List, Dict, Any
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from dotenv import load_dotenv

load_dotenv()

_client: AsyncQdrantClient | None = None

def get_qdrant() -> AsyncQdrantClient:
    global _client
    if _client is None:
        url = os.environ.get("QDRANT_URL")
        api_key = os.environ.get("QDRANT_API_KEY")
        if not url or not api_key:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set")
        _client = AsyncQdrantClient(url=url, api_key=api_key)
    return _client

async def upsert_chunks(
    collection_name: str,
    chunks: List[Dict[str, Any]],
    vectors: List[List[float]]
) -> None:
    """
    Upsert text chunks with embeddings into Qdrant.
    
    Args:
        collection_name: One of drug_clinical, drug_patent, drug_market, drug_regulatory
        chunks: List of dicts with keys: id, text, source_url, section, metadata
        vectors: List of 768-dim embedding vectors (same length as chunks)
    """
    client = get_qdrant()
    
    points = [
        PointStruct(
            id=chunk["id"],
            vector=vector,
            payload={
                "text": chunk["text"],
                "source_url": chunk.get("source_url", ""),
                "section": chunk.get("section", ""),
                "metadata": chunk.get("metadata", {})
            }
        )
        for chunk, vector in zip(chunks, vectors)
    ]
    
    await client.upsert(collection_name=collection_name, points=points)
    print(f"Upserted {len(points)} chunks to {collection_name}")

async def hybrid_search(
    collection_name: str,
    query_vector: List[float],
    query_text: str,
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Hybrid BM25 + vector search.
    
    For now, just doing vector search. Full BM25 requires Qdrant sparse vectors
    which need additional setup. This is sufficient for MVP.
    """
    client = get_qdrant()
    
    try:
        # Use query_points (new API) instead of search (deprecated)
        results = await client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit
        )
        
        return [
            {
                "id": hit.id,
                "score": hit.score,
                "text": hit.payload.get("text", ""),
                "source_url": hit.payload.get("source_url", ""),
                "section": hit.payload.get("section", ""),
                "metadata": hit.payload.get("metadata", {})
            }
            for hit in results.points
        ]
    except Exception as e:
        print(f"Qdrant search error: {e}. Returning empty results.")
        return []

async def get_collection_info(collection_name: str) -> Dict[str, Any]:
    """Get collection diagnostics"""
    client = get_qdrant()
    info = await client.get_collection(collection_name)
    return {
        "name": collection_name,
        "vectors_count": info.vectors_count,
        "points_count": info.points_count,
        "status": info.status
    }
