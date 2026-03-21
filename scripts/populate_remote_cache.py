"""
Script to populate REMOTE (Railway) Redis cache with pre-analyzed reports
Run this to cache Metformin, Ibuprofen, and Thalidomide on production
"""
import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def populate_remote_cache():
    # Import after setting up path
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    # Make sure we're using the production Redis URL
    redis_url = os.environ.get('UPSTASH_REDIS_REST_URL', 'NOT SET')
    print(f"Using Redis URL: {redis_url[:50]}..." if len(redis_url) > 50 else f"Using Redis URL: {redis_url}")
    
    from backend.memory.report_cache import report_cache
    
    # Map session IDs to molecule names
    reports = {
        "47eb22f0-009d-4d8a-b950-284ba1c4f1a5.json": "METFORMIN",
        "517241fc-6dc3-4dbf-964d-5ab5300fdca3.json": "IBUPROFEN",
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
        ttl = await report_cache.get_ttl(molecule)
        print(f"✅ Cached {molecule} (TTL: {ttl}s = {ttl/3600:.1f} hours)")
    
    print("\n🎉 Remote cache population complete!")
    print("Cached molecules: METFORMIN, IBUPROFEN, THALIDOMIDE")
    print("\nVerifying cache...")
    
    # Verify
    for molecule in ["METFORMIN", "IBUPROFEN", "THALIDOMIDE"]:
        exists = await report_cache.exists(molecule)
        print(f"  {molecule}: {'✅ CACHED' if exists else '❌ NOT FOUND'}")

if __name__ == "__main__":
    asyncio.run(populate_remote_cache())
