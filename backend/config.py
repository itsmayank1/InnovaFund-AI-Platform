import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "InnovaFund AI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Environment
    ENV: str = os.getenv("ENV", "development")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-in-production-innovafund-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 Hours
    
    # Database URLs
    POSTGRES_URL: str = os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@localhost:5433/funding_innovation_platform")
    MONGO_URL: str = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "funding_innovation_platform")
    
    # External API Keys (Optional with fallback handling)
    SERPAPI_KEY: str = os.getenv("SERPAPI_KEY", "")
    LENS_API_KEY: str = os.getenv("LENS_API_KEY", "")
    OPENALEX_MAILTO: str = os.getenv("OPENALEX_MAILTO", "admin@innovafund.ai")

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
