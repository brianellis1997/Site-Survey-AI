from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import logging
from PIL import Image
import io
import uuid

from ..agents.survey_workflow import SurveyAnalysisWorkflow
from ..database.vector_store import VectorStore
from ..config import settings

# Configure logging
logging.basicConfig(level=getattr(logging, settings.log_level.upper()))
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Site Survey AI",
    description="AI-powered site survey analysis for manufacturing equipment",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
survey_workflow: Optional[SurveyAnalysisWorkflow] = None
vector_store: Optional[VectorStore] = None


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    global survey_workflow, vector_store
    
    logger.info("Starting Site Survey AI application...")
    
    # Initialize the survey workflow
    survey_workflow = SurveyAnalysisWorkflow()
    await survey_workflow.initialize()
    
    # Initialize vector store separately for direct access
    vector_store = VectorStore()
    await vector_store.initialize()
    
    logger.info("Application initialized successfully")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Site Survey AI is running",
        "version": "0.1.0",
        "status": "healthy"
    }


@app.get("/stats")
async def get_database_stats():
    """Get statistics about the survey database"""
    if not vector_store:
        raise HTTPException(status_code=500, detail="Vector store not initialized")
    
    stats = await vector_store.get_survey_stats()
    return stats


@app.post("/analyze-survey")
async def analyze_survey(
    images: List[UploadFile] = File(...),
    notes: Optional[str] = Form(None),
    survey_id: Optional[str] = Form(None)
):
    """
    Analyze a site survey with uploaded images and optional notes
    """
    if not survey_workflow:
        raise HTTPException(status_code=500, detail="Survey workflow not initialized")
    
    if not images:
        raise HTTPException(status_code=400, detail="At least one image is required")
    
    try:
        # Convert uploaded files to PIL Images
        pil_images = []
        for image_file in images:
            # Validate file type
            if not image_file.content_type.startswith("image/"):
                raise HTTPException(
                    status_code=400, 
                    detail=f"File {image_file.filename} is not a valid image"
                )
            
            # Read and convert to PIL Image
            image_data = await image_file.read()
            pil_image = Image.open(io.BytesIO(image_data))
            pil_images.append(pil_image)
        
        # Generate survey ID if not provided
        if not survey_id:
            survey_id = str(uuid.uuid4())
        
        # Run the analysis workflow
        logger.info(f"Starting analysis for survey {survey_id} with {len(pil_images)} images")
        
        result = await survey_workflow.run_survey_analysis(
            images=pil_images,
            text_notes=notes or "",
            survey_id=survey_id
        )
        
        # Return the analysis result
        return {
            "survey_id": survey_id,
            "status": result["overall_status"],
            "confidence_score": result["confidence_score"],
            "report": result["final_report"],
            "num_images_processed": len(pil_images),
            "component_analyses_count": len(result["component_analyses"]),
            "similar_surveys_found": {
                "passing": len(result["similar_surveys"].get("passing_examples", [])),
                "failing": len(result["similar_surveys"].get("failing_examples", []))
            }
        }
        
    except Exception as e:
        logger.error(f"Error analyzing survey: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/survey/{survey_id}")
async def get_survey_result(survey_id: str):
    """
    Retrieve a previous survey result by ID
    """
    if not vector_store:
        raise HTTPException(status_code=500, detail="Vector store not initialized")
    
    try:
        # Search for the specific survey
        # This is a simplified approach - in production, you might want a dedicated metadata store
        results = await vector_store.collection.get(
            ids=[survey_id],
            include=["documents", "metadatas"]
        )
        
        if not results["ids"]:
            raise HTTPException(status_code=404, detail="Survey not found")
        
        return {
            "survey_id": survey_id,
            "report": results["documents"][0],
            "metadata": results["metadatas"][0]
        }
        
    except Exception as e:
        logger.error(f"Error retrieving survey {survey_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve survey: {str(e)}")


@app.get("/similar-surveys/{survey_id}")
async def find_similar_surveys(
    survey_id: str,
    limit: int = 5,
    status_filter: Optional[str] = None
):
    """
    Find surveys similar to a given survey ID
    """
    if not vector_store:
        raise HTTPException(status_code=500, detail="Vector store not initialized")
    
    try:
        # Get the target survey's embedding
        target_survey = await vector_store.collection.get(
            ids=[survey_id],
            include=["embeddings"]
        )
        
        if not target_survey["ids"]:
            raise HTTPException(status_code=404, detail="Survey not found")
        
        # Search for similar surveys
        similar_surveys = await vector_store.search_similar_surveys(
            query_embeddings=target_survey["embeddings"][0],
            n_results=limit,
            status_filter=status_filter
        )
        
        return {
            "target_survey_id": survey_id,
            "similar_surveys": similar_surveys
        }
        
    except Exception as e:
        logger.error(f"Error finding similar surveys for {survey_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to find similar surveys: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.site_survey_ai.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )