"""Centralized Application Configuration for SPECTRA-XDR."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings managed via environment variables and .env file."""

    # Application Core Config
    APP_NAME: str = "SPECTRA-XDR"
    APP_ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database Configuration (PostgreSQL Phase 2)
    DATABASE_URL: str = "postgresql+psycopg://spectra:spectra@localhost:5432/spectra_xdr"
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Wazuh XDR Telemetry (Phase 1 & 2.5)
    WAZUH_API_URL: str = "https://localhost:55000"
    WAZUH_USERNAME: str = "wazuh-wui"
    WAZUH_PASSWORD: str = "wazuh-password"
    WAZUH_VERIFY_SSL: bool = True
    WAZUH_TIMEOUT: int = 10
    WAZUH_INTEGRATION_TESTS: bool = False

    # Ollama Local LLM (Placeholder for local AI phase)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # Gemini Cloud LLM (Placeholder for cloud AI phase)
    GEMINI_API_KEY: str = ""

    # Redis Cache & Messaging (Placeholder for caching/queues phase)
    REDIS_URL: str = "redis://localhost:6379/0"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Global settings singleton
settings = Settings()
