"""
Configuration management for Site Survey AI application.

This module handles all configuration settings, loading from environment variables
and .env files with sensible defaults.
"""

import os
from pathlib import Path
from typing import Literal
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Model configuration
    model_name: str = Field(
        default="google/gemma-3n-E4B-it",
        description="Name of the AI model to use for analysis"
    )
    model_cache_dir: Path = Field(
        default=Path("./models"),
        description="Directory to cache downloaded models"
    )
    
    # Database configuration
    chroma_db_path: Path = Field(
        default=Path("./chroma_db"),
        description="Path to ChromaDB vector database storage"
    )
    
    # API configuration
    api_host: str = Field(
        default="0.0.0.0",
        description="Host address for the API server"
    )
    api_port: int = Field(
        default=8000,
        description="Port number for the API server",
        ge=1024,
        le=65535
    )
    
    # Logging configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level for the application"
    )
    
    @validator("model_cache_dir", "chroma_db_path")
    def ensure_directory_exists(cls, v):
        """Ensure required directories exist."""
        if isinstance(v, Path):
            v.mkdir(parents=True, exist_ok=True)
        return v
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }


# Global settings instance
settings = Settings()