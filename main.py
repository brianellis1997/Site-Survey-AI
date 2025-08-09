#!/usr/bin/env python3

import asyncio
import uvicorn
from src.site_survey_ai.config import settings

def main():
    """Main entry point for the Site Survey AI application"""
    print("🚀 Starting Site Survey AI...")
    print(f"📍 Server will run on {settings.api_host}:{settings.api_port}")
    print(f"🤖 Using model: {settings.model_name}")
    print(f"💾 ChromaDB path: {settings.chroma_db_path}")
    
    uvicorn.run(
        "src.site_survey_ai.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level=settings.log_level.lower()
    )

if __name__ == "__main__":
    main()