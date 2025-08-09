#!/usr/bin/env python3
"""
Simplified main.py that avoids problematic dependencies
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.site_survey_ai.config import settings

# Initialize FastAPI app
app = FastAPI(
    title="Site Survey AI",
    description="AI-powered site survey analysis for manufacturing equipment",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Site Survey AI is running",
        "version": "0.1.0",
        "status": "healthy",
        "model": settings.model_name
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "config": {
            "model_name": settings.model_name,
            "api_host": settings.api_host,
            "api_port": settings.api_port,
            "log_level": settings.log_level
        }
    }

@app.post("/analyze-survey")
async def analyze_survey():
    """Placeholder for survey analysis - will be implemented once dependencies are resolved"""
    return {
        "message": "Survey analysis endpoint - implementation in progress",
        "status": "placeholder"
    }

def main():
    """Main entry point for the Site Survey AI application"""
    print("🚀 Starting Site Survey AI (Simplified Version)...")
    print(f"📍 Server will run on {settings.api_host}:{settings.api_port}")
    print(f"🤖 Using model: {settings.model_name}")
    print(f"💾 ChromaDB path: {settings.chroma_db_path}")
    print("📝 Note: Using simplified version without complex ML dependencies")
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        reload=False,  # Disable reload to avoid subprocess issues
        log_level=settings.log_level.lower()
    )

if __name__ == "__main__":
    main()