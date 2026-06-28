from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Pull Request Review Assistant"
    
    # GitHub settings
    GITHUB_APP_ID: Optional[str] = None
    GITHUB_WEBHOOK_SECRET: Optional[str] = None
    GITHUB_PRIVATE_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/pr_reviewer"
    
    # LLM and Tracing
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "pr_reviewer"
    

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
