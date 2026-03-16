import os
from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

_embedder: GoogleGenerativeAIEmbeddings | None = None

def get_embedder() -> GoogleGenerativeAIEmbeddings:
    global _embedder
    if _embedder is None:
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY must be set")
        _embedder = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=api_key
        )
    return _embedder

async def embed_chunks(chunks: List[str]) -> List[List[float]]:
    """
    Embed text chunks using Gemini embedding-001.
    
    Args:
        chunks: List of text strings to embed
        
    Returns:
        List of 768-dimensional embedding vectors
    """
    embedder = get_embedder()
    
    # Batch in groups of 100 to avoid rate limits
    batch_size = 100
    all_embeddings = []
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        embeddings = await embedder.aembed_documents(batch)
        all_embeddings.extend(embeddings)
        print(f"Embedded batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")
    
    return all_embeddings
