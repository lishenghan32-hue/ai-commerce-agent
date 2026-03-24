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
    debug: bool = False  # 生产环境应设为 False

    # CORS - 允许的前端域名
    cors_origins: list = ["http://localhost:8000", "http://127.0.0.1:8000"]

    # Database (SQLite for local development)
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./test.db"
    )

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # Celery
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")

    # LLM API
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    minimax_api_key: str = os.getenv("MINIMAX_API_KEY", "")
    default_llm_provider: str = os.getenv("DEFAULT_LLM_PROVIDER", "openai")  # openai or anthropic

    # Crawler
    xhs_cookie: str = os.getenv("XHS_COOKIE", "")
    xhs_user_agent: str = os.getenv("XHS_USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    # PPT
    ppt_output_dir: str = os.getenv("PPT_OUTPUT_DIR", "./output/ppt")

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings"""
    return Settings()


settings = get_settings()
