#!/usr/bin/env python3
"""
Simple test API to verify basic functionality
"""

from fastapi import FastAPI
import uvicorn
from src.site_survey_ai.config import settings

# Create a minimal FastAPI app for testing
app = FastAPI(
    title="Site Survey AI - Test",
    description="Basic test API to verify setup",
    version="0.1.0"
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Site Survey AI Test Server is running",
        "status": "healthy",
        "model_name": settings.model_name,
        "api_port": settings.api_port
    }

@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify functionality"""
    return {
        "test": "success",
        "config_loaded": True,
        "dependencies": "minimal"
    }

if __name__ == "__main__":
    print(f"🚀 Starting test server on {settings.api_host}:{settings.api_port}")
    print(f"📍 Access at: http://localhost:{settings.api_port}")
    
    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower()
    )