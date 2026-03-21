"""
Script to populate Redis cache with pre-analyzed reports
Run this once to cache Metformin, Ibuprofen, and Thalidomide
"""
import asyncio
import json
import os
from pathlib import Path

async def populate_cache():
    # Import after setting up path
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from backend.memory.report_cache import report_cache
    
    # Map session IDs to molecule names
    reports = {
        "47eb22f0-009d-4d8a-b950-284ba1c4f1a5.json": "METFORMIN",
        "517241fc-6dc3-4dbf-964d-5ab5300fdca3.json": "IBUPROFEN",
        "cba8df2f-7a11-409b-833a-ccf9b76fc65e.json": "METFORMIN",  # duplicate
        "ec27bd24-5b9e-4670-a923-2ed56de090b4.json": "THALIDOMIDE"
    }
    
    tmp_reports_dir = Path(__file__).parent.parent / "tmp_reports"
    
    for filename, molecule in reports.items():
        filepath = tmp_reports_dir / filename
        if not filepath.exists():
            print(f"⚠️  {filename} not found, skipping...")
            continue
        
        with open(filepath, "r") as f:
            report_data = json.load(f)
        
        # Cache the report
        await report_cache.set(molecule, report_data)
        print(f"✅ Cached {molecule} from {filename}")
    
    print("\n🎉 Cache population complete!")
    print("Cached molecules: METFORMIN, IBUPROFEN, THALIDOMIDE")

if __name__ == "__main__":
    asyncio.run(populate_cache())
