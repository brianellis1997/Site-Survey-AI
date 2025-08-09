from typing import List, Dict, Any, Optional, Tuple
import chromadb
from chromadb.config import Settings as ChromaSettings
import numpy as np
import logging
from pathlib import Path
import json
from datetime import datetime

from ..config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    def __init__(self, collection_name: str = "site_surveys"):
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        
    async def initialize(self):
        logger.info(f"Initializing ChromaDB at {settings.chroma_db_path}")
        
        settings.chroma_db_path.mkdir(exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(settings.chroma_db_path),
            settings=ChromaSettings(
                anonymized_telemetry=False
            )
        )
        
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Site survey historical data for RAG"}
        )
        
        logger.info(f"Collection '{self.collection_name}' ready with {self.collection.count()} documents")
    
    async def add_survey_record(
        self,
        survey_id: str,
        image_embeddings: List[float],
        metadata: Dict[str, Any],
        analysis_result: str,
        status: str  # "pass" or "fail"
    ):
        if not self.collection:
            await self.initialize()
        
        document_metadata = {
            **metadata,
            "survey_id": survey_id,
            "analysis_result": analysis_result,
            "status": status,
            "timestamp": datetime.now().isoformat(),
        }
        
        self.collection.add(
            embeddings=[image_embeddings],
            documents=[analysis_result],
            metadatas=[document_metadata],
            ids=[survey_id]
        )
        
        logger.info(f"Added survey record {survey_id} with status: {status}")
    
    async def search_similar_surveys(
        self,
        query_embeddings: List[float],
        n_results: int = 5,
        status_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        if not self.collection:
            await self.initialize()
        
        where_clause = {}
        if status_filter:
            where_clause["status"] = status_filter
        
        results = self.collection.query(
            query_embeddings=[query_embeddings],
            n_results=n_results,
            where=where_clause if where_clause else None,
            include=["documents", "metadatas", "distances"]
        )
        
        similar_surveys = []
        for i in range(len(results["ids"][0])):
            similar_surveys.append({
                "survey_id": results["ids"][0][i],
                "analysis": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "similarity_score": 1 - results["distances"][0][i]  # Convert distance to similarity
            })
        
        return similar_surveys
    
    async def get_survey_stats(self) -> Dict[str, Any]:
        if not self.collection:
            await self.initialize()
        
        total_count = self.collection.count()
        
        # Get all metadata to calculate pass/fail ratios
        all_results = self.collection.get(include=["metadatas"])
        
        pass_count = sum(1 for meta in all_results["metadatas"] if meta.get("status") == "pass")
        fail_count = sum(1 for meta in all_results["metadatas"] if meta.get("status") == "fail")
        
        return {
            "total_surveys": total_count,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_rate": pass_count / total_count if total_count > 0 else 0
        }
    
    async def delete_survey(self, survey_id: str):
        if not self.collection:
            await self.initialize()
        
        self.collection.delete(ids=[survey_id])
        logger.info(f"Deleted survey record {survey_id}")