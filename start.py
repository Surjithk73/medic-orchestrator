#!/usr/bin/env python3
"""
Railway startup script that handles PORT environment variable
"""
import os
import sys

if __name__ == "__main__":
    try:
        port = os.environ.get("PORT", "8000")
        print(f"Starting server on port {port}...")
        
        # Import uvicorn
        import uvicorn
        
        # Run the app
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=int(port),
            log_level="info"
        )
    except Exception as e:
        print(f"FATAL ERROR during startup: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
