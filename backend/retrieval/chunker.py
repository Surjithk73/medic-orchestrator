import re
from typing import List, Dict

def chunk_by_semantic_boundary(text: str, max_tokens: int = 500) -> List[Dict[str, any]]:
    """
    Split text by semantic boundaries (section headers, paragraph breaks).
    
    Args:
        text: Input text to chunk
        max_tokens: Maximum tokens per chunk (rough estimate: 1 token ≈ 4 chars)
        
    Returns:
        List of dicts with keys: text, section, char_offset, estimated_tokens
    """
    chunks = []
    
    # Split on double newlines (paragraph boundaries)
    paragraphs = re.split(r'\n\n+', text)
    
    current_chunk = ""
    current_offset = 0
    section = "main"
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
            
        # Check if this looks like a section header (all caps, short, ends with colon, etc.)
        if len(para) < 100 and (para.isupper() or para.endswith(':') or re.match(r'^#+\s+', para)):
            # Save current chunk if it exists
            if current_chunk:
                chunks.append({
                    "text": current_chunk.strip(),
                    "section": section,
                    "char_offset": current_offset,
                    "estimated_tokens": len(current_chunk) // 4
                })
                current_offset += len(current_chunk)
                current_chunk = ""
            
            # Update section name
            section = para.strip('#: ')
            continue
        
        # Estimate tokens (rough: 1 token ≈ 4 chars)
        para_tokens = len(para) // 4
        current_tokens = len(current_chunk) // 4
        
        if current_tokens + para_tokens > max_tokens and current_chunk:
            # Save current chunk
            chunks.append({
                "text": current_chunk.strip(),
                "section": section,
                "char_offset": current_offset,
                "estimated_tokens": current_tokens
            })
            current_offset += len(current_chunk)
            current_chunk = ""
        
        current_chunk += para + "\n\n"
    
    # Save final chunk
    if current_chunk:
        chunks.append({
            "text": current_chunk.strip(),
            "section": section,
            "char_offset": current_offset,
            "estimated_tokens": len(current_chunk) // 4
        })
    
    # Filter out chunks that are too large (hard cap)
    chunks = [c for c in chunks if c["estimated_tokens"] <= max_tokens]
    
    return chunks
