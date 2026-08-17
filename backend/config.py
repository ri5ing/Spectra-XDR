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

    # Database Configuration (Placeholder for future database phase)
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/spectra_xdr"

    # Wazuh XDR Telemetry (Placeholder for Wazuh phase)
    WAZUH_API_URL: str = "https://localhost:55000"
    WAZUH_USERNAME: str = "wazuh-wui"
    WAZUH_PASSWORD: str = "wazuh-password"
    WAZUH_VERIFY_SSL: bool = True
    WAZUH_TIMEOUT: int = 10

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
