import json
from typing import Annotated, List, Optional
from pydantic_settings import BaseSettings, NoDecode
from pydantic import AnyHttpUrl, validator

# Development-only defaults; override via environment / backend/.env in any real deployment
DEFAULT_SECRET_KEY = "DEVELOPMENT_SECRET_KEY_CHANGE_ME_NOW"
DEFAULT_ENCRYPTION_KEY = "zY8_6t6O9xW7p5lS0k3N2M1V4B5z7X8c9v0="

class Settings(BaseSettings):
    # Base
    PROJECT_NAME: str = "MentalFlow"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = DEFAULT_SECRET_KEY
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    ENCRYPTION_KEY: str = DEFAULT_ENCRYPTION_KEY # master key, stretched with PBKDF2
    
    # Core Database
    # Fallback to SQLite if PostgreSQL is not reachabe/configured for local dev
    DATABASE_URL: str = "sqlite:///./mentalflow.db"
    DATABASE_ECHO: bool = False
    
    # CORS
    # NoDecode: accept a plain comma-separated string (the validator splits it) as well as a JSON list
    CORS_ORIGINS: Annotated[List[str], NoDecode] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and v.strip().startswith("["):
            return json.loads(v)
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Demo mode: seed a demo account on first start and let unauthenticated
    # requests to the patient endpoints act as that account. Disable in production.
    DEMO_MODE: bool = True
    DEMO_USER_EMAIL: str = "demo@example.com"
    DEMO_USER_PASSWORD: Optional[str] = None  # random (logged once) if not set

    # AI & ML Configuration
    GROQ_API_KEY: Optional[str] = None
    RL_MODEL_PATH: str = "/models/rl_agent.pt"
    RL_TRAINING_ENABLED: bool = True
    RL_UPDATE_FREQUENCY: int = 7 # days

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
