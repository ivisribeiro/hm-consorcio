from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://crm_user:password@localhost:5432/crm_db"

    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # SMTP (opcional)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Redis (opcional - desabilitado se não configurado)
    REDIS_URL: Optional[str] = None

    # App
    APP_NAME: str = "CRM Consórcios"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # CORS - URLs permitidas (separadas por vírgula)
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> list:
        """Retorna lista de origens CORS permitidas"""
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        # Em produção, adiciona URLs de deploy automaticamente
        if not self.DEBUG:
            origins.append("https://*.onrender.com")
            origins.append("https://*.railway.app")
            origins.append("https://*.up.railway.app")
        return origins

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignora variáveis extras do ambiente


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
