#!/usr/bin/env python3
"""
Railway startup script that handles PORT environment variable
"""
import os
import sys

if __name__ == "__main__":
    try:
        # Railway sets PORT, default to 8000 for local
        port = int(os.environ.get("PORT", "8000"))
        host = "0.0.0.0"
        
        print(f"Starting Medic Orchestrator on {host}:{port}...")
        print(f"Environment: {'Railway' if 'RAILWAY_ENVIRONMENT' in os.environ else 'Local'}")
        
        # Import uvicorn
        import uvicorn
        
        # Run the app with explicit parameters
        uvicorn.run(
            "backend.main:app",
            host=host,
            port=port,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"FATAL ERROR during startup: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
