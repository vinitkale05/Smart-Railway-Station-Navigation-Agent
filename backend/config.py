import os
from pathlib import Path
from typing import List
from pydantic import BaseModel

# Automatically load .env if present
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

class Settings(BaseModel):
    PROJECT_NAME: str = "Smart Railway Station Navigation Agent"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Security
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "station_admin")
    ADMIN_PASSWORD_HASH: str = os.getenv("ADMIN_PASSWORD_HASH", "admin123")  # Demo default
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key-mit-adt-ai-project-2026")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24  # 24 hours
    
    # LLM Settings (Gemini Flash API - read from .env or environment)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./railway_station.db")
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    
    # Agent Guardrails
    MAX_TOOL_CALLS_PER_TURN: int = 6
    REQUEST_TIMEOUT_SECONDS: int = 15

settings = Settings()
