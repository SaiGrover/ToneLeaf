"""Expose Toneleaf's FastAPI app as a Vercel Python Function."""

from backend.main import app

__all__ = ["app"]
