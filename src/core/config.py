from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "SportSee RAG"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    
    # Mistral
    MISTRAL_API_KEY: str
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/sportsee.db"
    
    # Monitoring
    LOGFIRE_TOKEN: Optional[str] = None
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
