#!/usr/bin/env python3
"""
Quick test API on port 8001
"""

from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Site Survey AI - Quick Test")

@app.get("/")
async def root():
    return {"message": "Site Survey AI Test is working", "status": "healthy"}

@app.get("/health")
async def health():
    return {"status": "ok", "port": 8001}

if __name__ == "__main__":
    print("🚀 Starting quick test server on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")