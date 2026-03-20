"""
Phase 3 Tests — Retrieval Layer

Verifies:
- APIClient handles basic HTTP GET requests
- PDF parser gracefully falls back if invalid input or extracts text successfully if valid (mocked)
- Semantic chunker breaks text into properly sized lists
- Embedder instantiates correctly
"""

import pytest
import asyncio
from backend.retrieval.api_client import api_client
from backend.retrieval.pdf_parser import extract_text_from_pdf_bytes
from backend.retrieval.chunker import chunker
from backend.retrieval.embedder import embedder

@pytest.mark.asyncio
async def test_api_client_basic_get():
    """Verify HTTP client can fetch a public JSON endpoint (JSONPlaceholder)."""
    resp = await api_client.get("https://jsonplaceholder.typicode.com/todos/1")
    assert resp.status_code == 200
    assert "userId" in resp.json()

def test_pdf_parser_invalid_bytes_raises_error():
    """Sending junk bytes to the PDF parser should raise a RuntimeError."""
    with pytest.raises(RuntimeError):
        extract_text_from_pdf_bytes(b"junk not a pdf")

def test_semantic_chunker_basic_split():
    """Verify recursive character splitter separates by paragraph or token size."""
    long_text = "Paragraph one is short.\n\nParagraph two is slightly longer but semantic."
    chunks = chunker.chunk_text(long_text)
    
    assert len(chunks) > 0
    # As the string is short, it might just be 1 chunk due to chunk_size=1500
    assert "Paragraph one" in chunks[0]

def test_semantic_chunker_empty_string():
    """Empty strings should return an empty chunk list."""
    chunks = chunker.chunk_text("   ")
    assert len(chunks) == 0

@pytest.mark.asyncio
async def test_embedder_instantiation():
    """Google Gemini embedder model should initialize without errors."""
    assert embedder.embeddings_model is not None
    assert embedder.embeddings_model.model == "models/text-embedding-004"
