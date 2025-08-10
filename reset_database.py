#!/usr/bin/env python3
"""
Reset the ChromaDB database to fix embedding dimension issues
"""

import shutil
import asyncio
from pathlib import Path

async def reset_database():
    """Reset the ChromaDB database"""
    
    print("🔄 Resetting Site Survey AI database...")
    
    db_path = Path("chroma_db")
    
    if db_path.exists():
        try:
            shutil.rmtree(db_path)
            print(f"✅ Removed old database: {db_path}")
        except Exception as e:
            print(f"❌ Error removing database: {e}")
            return False
    
    print("🆕 Database reset complete. The system will create a fresh database on next startup.")
    return True

if __name__ == "__main__":
    asyncio.run(reset_database())