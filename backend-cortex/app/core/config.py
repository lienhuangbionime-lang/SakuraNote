from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pathlib import Path

# Get project root (backend-cortex)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"

class Settings(BaseSettings):
    # 定義變數 (Pydantic 會自動從環境變數讀取)
    GEMINI_API_KEY: str
    
    # Optional fields with defaults
    MODEL_SMART: str = "gemini-2.5-flash"
    PROJECT_NAME: str = "LifeOS Cortex"
    API_V1_STR: str = "/api/v1"
    
    # Validator to ensure defaults act as fallbacks if env var is missing or empty
    @property
    def GEMINI_SMART_MODEL(self):
        return self.MODEL_SMART
        
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH), 
        env_file_encoding="utf-8",
        extra="ignore" # 忽略多餘的變數
    )

settings = Settings()
