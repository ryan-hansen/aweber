"""Main entry point for the Widget CRUD API."""

import os

import uvicorn

if __name__ == "__main__":
    # Use localhost by default for security, allow override via environment
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))

    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=True,
        log_level="info",
    )
