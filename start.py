#!/usr/bin/env python3
"""
Railway startup script that handles PORT environment variable
"""
import os
import sys

if __name__ == "__main__":
    port = os.environ.get("PORT", "8000")
    
    # Import uvicorn
    import uvicorn
    
    # Run the app
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=int(port),
        log_level="info"
    )
