"""FUTRSEC Root ASGI Entry Point.

Enables starting the server with either:
  `uvicorn app.main:app` OR `uvicorn main:app`
when running from the workspace root directory (V:\\ai_jobagent).
"""

from app.main import app

__all__ = ["app"]
