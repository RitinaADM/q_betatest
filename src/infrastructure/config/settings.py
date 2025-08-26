from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    database_url: str = Field(
        default="sqlite+aiosqlite:///./items.db",
        description="Database connection URL"
    )
    database_echo: bool = Field(
        default=False,
        description="Enable SQLAlchemy query logging"
    )


class AppSettings(BaseSettings):
    """Application configuration settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    app_name: str = Field(
        default="FastAPI Hexagonal Architecture",
        description="Application name"
    )
    app_version: str = Field(
        default="2.0.0",
        description="Application version"
    )
    app_description: str = Field(
        default="A FastAPI application implementing hexagonal architecture",
        description="Application description"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )


class ServerSettings(BaseSettings):
    """Server configuration settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    host: str = Field(
        default="0.0.0.0",
        description="Server host"
    )
    port: int = Field(
        default=8000,
        description="Server port"
    )
    log_level: str = Field(
        default="info",
        description="Logging level"
    )


class Settings(BaseSettings):
    """Combined application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    # Nested settings
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    app: AppSettings = Field(default_factory=AppSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)


# Global settings instance
settings = Settings()