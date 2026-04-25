from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    # Base
    PROJECT_NAME: str = "MentalFlow"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "DEVELOPMENT_SECRET_KEY_CHANGE_ME_NOW"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    ENCRYPTION_KEY: str = "zY8_6t6O9xW7p5lS0k3N2M1V4B5z7X8c9v0=" # 32-byte b64 key
    
    # Core Database
    # Fallback to SQLite if PostgreSQL is not reachabe/configured for local dev
    DATABASE_URL: str = "sqlite:///./mentalflow.db"
    DATABASE_ECHO: bool = False
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str] | str:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # AI & ML Configuration
    GROQ_API_KEY: Optional[str] = None
    RL_MODEL_PATH: str = "/models/rl_agent.pt"
    RL_TRAINING_ENABLED: bool = True
    RL_UPDATE_FREQUENCY: int = 7 # days

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
