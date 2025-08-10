#!/usr/bin/env python3
"""
Site Survey AI - Main Application Entry Point

This is the primary entry point for the Site Survey AI application.
It automatically detects available dependencies and runs the appropriate version.
"""

import sys
import logging
from pathlib import Path
from typing import Optional, List

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import configuration
try:
    from src.site_survey_ai.config import settings
except ImportError as e:
    print(f"❌ Error importing configuration: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import complex dependencies
ml_dependencies_available = True
ml_import_error = None

try:
    from src.site_survey_ai.agents.survey_workflow import SurveyAnalysisWorkflow
    from src.site_survey_ai.database.vector_store import VectorStore
    from PIL import Image
    import io
    import uuid
except ImportError as e:
    ml_dependencies_available = False
    ml_import_error = str(e)
    logger.warning(f"ML dependencies not available: {e}")
    logger.info("Running in simplified mode without ML features")

# Initialize FastAPI app
app = FastAPI(
    title="Site Survey AI",
    description="AI-powered site survey analysis for manufacturing equipment",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances (only if ML dependencies are available)
survey_workflow: Optional[object] = None
vector_store: Optional[object] = None


@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup"""
    global survey_workflow, vector_store
    
    logger.info("🚀 Starting Site Survey AI application...")
    logger.info(f"📍 Server running on {settings.api_host}:{settings.api_port}")
    logger.info(f"🤖 Using model: {settings.model_name}")
    logger.info(f"💾 ChromaDB path: {settings.chroma_db_path}")
    
    if ml_dependencies_available:
        try:
            logger.info("🧠 Initializing ML components...")
            # Initialize the survey workflow
            survey_workflow = SurveyAnalysisWorkflow()
            await survey_workflow.initialize()
            
            # Initialize vector store separately for direct access
            vector_store = VectorStore()
            await vector_store.initialize()
            
            logger.info("✅ ML components initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize ML components: {e}")
            logger.info("🔄 Falling back to simplified mode")
            survey_workflow = None
            vector_store = None
    else:
        logger.info("📝 Running in simplified mode")
        logger.info(f"   Reason: {ml_import_error}")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Site Survey AI is running",
        "version": "0.1.0",
        "status": "healthy",
        "mode": "full" if ml_dependencies_available and survey_workflow else "simplified",
        "model": settings.model_name
    }


@app.get("/health")
async def health_check():
    """Detailed health check"""
    health_status = {
        "status": "healthy",
        "mode": "full" if ml_dependencies_available and survey_workflow else "simplified",
        "config": {
            "model_name": settings.model_name,
            "api_host": settings.api_host,
            "api_port": settings.api_port,
            "log_level": settings.log_level,
            "chroma_db_path": str(settings.chroma_db_path)
        },
        "features": {
            "ml_dependencies": ml_dependencies_available,
            "survey_workflow": survey_workflow is not None,
            "vector_store": vector_store is not None,
        }
    }
    
    if not ml_dependencies_available:
        health_status["warnings"] = [
            f"ML dependencies not available: {ml_import_error}",
            "Running in simplified mode"
        ]
    
    return health_status


@app.get("/stats")
async def get_database_stats():
    """Get statistics about the survey database"""
    if not vector_store:
        return JSONResponse(
            status_code=503,
            content={
                "error": "Vector store not available",
                "message": "Application running in simplified mode"
            }
        )
    
    try:
        stats = await vector_store.get_survey_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


@app.post("/analyze-survey")
async def analyze_survey(
    images: Optional[List[UploadFile]] = File(None),
    notes: Optional[str] = Form(None),
    survey_id: Optional[str] = Form(None)
):
    """
    Analyze a site survey with uploaded images and optional notes
    """
    if not survey_workflow:
        return JSONResponse(
            status_code=503,
            content={
                "error": "Survey analysis not available",
                "message": "Application running in simplified mode",
                "suggestion": "Install required ML dependencies for full functionality",
                "mode": "simplified"
            }
        )
    
    if not images:
        return JSONResponse(
            status_code=200,
            content={
                "message": "Survey analysis endpoint - ready to receive images",
                "status": "awaiting_input",
                "expected_input": {
                    "images": "List of image files (required)",
                    "notes": "Optional text notes",
                    "survey_id": "Optional survey identifier"
                }
            }
        )
    
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
    """Retrieve a previous survey result by ID"""
    if not vector_store:
        raise HTTPException(
            status_code=503, 
            detail="Vector store not available - running in simplified mode"
        )
    
    try:
        # Search for the specific survey
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


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "detail": str(exc) if settings.log_level == "DEBUG" else "Enable DEBUG logging for details"
        }
    )


def main():
    """Main entry point for the Site Survey AI application"""
    print("🚀 Starting Site Survey AI...")
    print(f"📍 Server will run on {settings.api_host}:{settings.api_port}")
    print(f"🤖 Using model: {settings.model_name}")
    print(f"💾 ChromaDB path: {settings.chroma_db_path}")
    
    if not ml_dependencies_available:
        print("📝 Note: Running in simplified mode")
        print(f"   Missing dependencies: {ml_import_error}")
        print("   Install ML dependencies for full functionality")
    
    try:
        uvicorn.run(
            app,
            host=settings.api_host,
            port=settings.api_port,
            reload=False,  # Disable reload to avoid subprocess issues
            log_level=settings.log_level.lower(),
            access_log=True
        )
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()