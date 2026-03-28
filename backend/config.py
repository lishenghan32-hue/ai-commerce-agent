"""
Configuration management
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # App
    app_name: str = "AI Commerce Insight Generator"
    debug: bool = False

    # CORS - 允许的前端域名
    cors_origins: list = ["http://localhost:8000", "http://127.0.0.1:8000"]

    # MiniMax API (currently used LLM)
    minimax_api_key: str = os.getenv("MINIMAX_API_KEY", "")

    # Crawler
    xhs_cookie: str = os.getenv("XHS_COOKIE", "")
    xhs_user_agent: str = os.getenv("XHS_USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings"""
    return Settings()


settings = get_settings()
