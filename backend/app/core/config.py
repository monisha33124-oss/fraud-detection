from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "Fraud Detection System API"
    API_V1_STR: str = "/api/v1"
    
    # Security
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Database
    DATABASE_URL: str
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://127.0.0.1:5173", "http://127.0.0.1:5174", "http://localhost:3000"]
    
    # Fraud Thresholds
    RISK_THRESHOLD_MEDIUM: int = 30
    RISK_THRESHOLD_HIGH: int = 60
    RISK_THRESHOLD_CRITICAL: int = 80
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()
