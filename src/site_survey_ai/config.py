import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_name: str = "google/paligemma-3b-pt-224"
    model_cache_dir: Path = Path("./models")
    
    chroma_db_path: Path = Path("./chroma_db")
    
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    log_level: str = "INFO"
    
    model_config = {"env_file": ".env"}


settings = Settings()