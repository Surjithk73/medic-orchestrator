"""
scripts/setup_qdrant.py
Creates the 4 domain vector collections in Qdrant Cloud.
Run once: python scripts/setup_qdrant.py
"""

import os
import sys
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, OptimizersConfigDiff

load_dotenv()

QDRANT_URL = os.environ["QDRANT_URL"]
QDRANT_API_KEY = os.environ["QDRANT_API_KEY"]

COLLECTIONS = [
    "drug_clinical",
    "drug_patent",
    "drug_market",
    "drug_regulatory",
]

VECTOR_SIZE = 3072         # Gemini embedding-001 output dimensions
DISTANCE    = Distance.COSINE


def create_collections():
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=30)

    existing = {c.name for c in client.get_collections().collections}
    print(f"Existing collections: {existing or 'none'}")

    for name in COLLECTIONS:
        if name in existing:
            print(f"  ✓ '{name}' already exists — skipping")
            continue

        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=VECTOR_SIZE, distance=DISTANCE),
            optimizers_config=OptimizersConfigDiff(
                default_segment_number=2,      # Good for < 1M vectors
            ),
        )
        print(f"  ✅ Created collection '{name}' ({VECTOR_SIZE}-dim, COSINE)")

    # Verify
    print("\nVerification:")
    for name in COLLECTIONS:
        info = client.get_collection(name)
        size = info.config.params.vectors.size
        status = info.status
        points = info.points_count
        print(f"  {name}: size={size}, status={status}, points={points}")

    print("\nQdrant setup complete ✅")


if __name__ == "__main__":
    create_collections()
