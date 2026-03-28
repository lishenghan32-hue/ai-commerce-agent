"""
AI Service - Unified entry point
"""
from functools import lru_cache

from backend.services.ai.base import AIService

__all__ = ["get_ai_service"]


@lru_cache()
def get_ai_service() -> AIService:
    """Get singleton AIService instance"""
    return AIService()
