"""
Media Player Backend Server Runner
Usage:
    python run.py
"""

import os
import uvicorn
from app.config import settings

if __name__ == "__main__":
    port = int(os.getenv("PORT", settings.PORT))
    host = os.getenv("HOST", "0.0.0.0")
    print(f">> Starting {settings.APP_NAME} on http://{host}:{port}")
    print(f">> Interactive Swagger UI: http://{host}:{port}/docs")
    print(f">> Interactive ReDoc UI:   http://{host}:{port}/redoc")
    uvicorn.run("app.main:app", host=host, port=port, reload=False)
