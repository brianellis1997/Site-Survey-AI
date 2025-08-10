#!/usr/bin/env python3
"""
Load survey knowledge base into ChromaDB for Site Survey AI
"""

import os
import sys
import asyncio
from pathlib import Path
from typing import List

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.site_survey_ai.database.vector_store import VectorStore
from src.site_survey_ai.config import settings

async def load_knowledge_base_documents():
    """Load knowledge base documents into ChromaDB"""
    
    print("📚 Loading Site Survey Knowledge Base...")
    
    # Initialize vector store
    vector_store = VectorStore()
    await vector_store.initialize()
    
    knowledge_base_dir = Path("survey_knowledge_base")
    
    if not knowledge_base_dir.exists():
        print("❌ survey_knowledge_base directory not found!")
        return
    
    documents_loaded = 0
    
    # Load all markdown files from knowledge base
    for file_path in knowledge_base_dir.glob("*.md"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create a unique document ID
            doc_id = f"knowledge_base_{file_path.stem}"
            
            # Add to ChromaDB with metadata
            metadata = {
                "document_type": "knowledge_base",
                "source_file": str(file_path),
                "category": "guidelines" if "guidelines" in file_path.name else "past_survey",
                "loaded_date": "2025-08-10"
            }
            
            # Store in ChromaDB
            vector_store.collection.add(
                ids=[doc_id],
                documents=[content],
                metadatas=[metadata]
            )
            
            print(f"✅ Loaded: {file_path.name}")
            documents_loaded += 1
            
        except Exception as e:
            print(f"❌ Error loading {file_path.name}: {e}")
    
    # Get updated stats
    stats = await vector_store.get_survey_stats()
    
    print(f"\n📊 Knowledge Base Summary:")
    print(f"   Documents loaded this session: {documents_loaded}")
    print(f"   Total documents in database: {stats.get('total_surveys', 'Unknown')}")
    print(f"   Database location: {settings.chroma_db_path}")
    
    print(f"\n🚀 Knowledge base is now ready for Site Survey AI!")
    print(f"   The system will reference these documents when analyzing new surveys.")

async def main():
    """Main function"""
    try:
        await load_knowledge_base_documents()
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"   Make sure the Site Survey AI environment is properly set up.")

if __name__ == "__main__":
    asyncio.run(main())