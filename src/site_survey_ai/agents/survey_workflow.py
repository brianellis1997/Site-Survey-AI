"""
Site Survey AI - Survey Analysis Workflow

This module implements the main analysis workflow using LangGraph for
orchestrating a multi-step site survey inspection process.
"""

from typing import List, Dict, Any, TypedDict, Annotated, Optional
import operator
import logging
import re
import uuid
from langgraph.graph import StateGraph, END
from PIL import Image

from ..models.multimodal_model import MultimodalModel
from ..database.vector_store import VectorStore
from ..utils.image_processor import ImageProcessor

logger = logging.getLogger(__name__)


class SurveyState(TypedDict):
    """State definition for the survey analysis workflow."""
    images: List[Image.Image]
    text_notes: str
    survey_id: str
    component_analyses: Annotated[List[Dict[str, Any]], operator.add]
    similar_surveys: List[Dict[str, Any]]
    final_report: str
    overall_status: str  # "pass" or "fail"
    confidence_score: float


class SurveyAnalysisWorkflow:
    """
    Main workflow orchestrator for site survey analysis.
    
    Implements a 5-step analysis pipeline using LangGraph:
    1. Image preprocessing
    2. Component-level analysis
    3. Historical survey retrieval
    4. Report generation
    5. Validation and scoring
    """
    
    def __init__(self) -> None:
        """Initialize the workflow with required components."""
        self.multimodal_model = MultimodalModel()
        self.vector_store = VectorStore()
        self.image_processor = ImageProcessor()
        self.workflow: Optional[StateGraph] = None
        
    async def initialize(self):
        await self.multimodal_model.load_model()
        await self.vector_store.initialize()
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(SurveyState)
        
        # Add nodes
        workflow.add_node("process_images", self.process_images_node)
        workflow.add_node("analyze_components", self.analyze_components_node)
        workflow.add_node("retrieve_similar", self.retrieve_similar_surveys_node)
        workflow.add_node("generate_report", self.generate_report_node)
        workflow.add_node("validate_checklist", self.validate_checklist_node)
        
        # Define the flow
        workflow.set_entry_point("process_images")
        workflow.add_edge("process_images", "analyze_components")
        workflow.add_edge("analyze_components", "retrieve_similar")
        workflow.add_edge("retrieve_similar", "generate_report")
        workflow.add_edge("generate_report", "validate_checklist")
        workflow.add_edge("validate_checklist", END)
        
        return workflow.compile()
    
    async def process_images_node(self, state: SurveyState) -> Dict[str, Any]:
        logger.info(f"Processing {len(state['images'])} images for survey {state['survey_id']}")
        
        processed_images = []
        for image in state["images"]:
            processed_img = await self.image_processor.preprocess_image(image)
            processed_images.append(processed_img)
        
        return {"images": processed_images}
    
    async def analyze_components_node(self, state: SurveyState) -> Dict[str, Any]:
        logger.info("Analyzing individual components in images")
        
        component_analyses = []
        
        for i, image in enumerate(state["images"]):
            # Create analysis prompt for each image
            analysis_prompt = f"""
            Analyze this industrial/manufacturing equipment image for a site survey inspection.
            
            Additional context: {state.get('text_notes', 'No additional notes provided.')}
            
            Please identify:
            1. What type of equipment/component is shown
            2. Visible condition of bolts, fasteners, connections
            3. Any signs of wear, damage, corrosion, or misalignment
            4. Overall component condition assessment
            5. Any safety concerns or anomalies
            
            Provide a structured analysis with specific observations.
            """
            
            analysis_result = await self.multimodal_model.analyze_image(image, analysis_prompt)
            
            component_analyses.append({
                "image_index": i,
                "analysis": analysis_result,
                "image_embedding": await self.image_processor.get_image_embedding(image)
            })
        
        return {"component_analyses": component_analyses}
    
    async def retrieve_similar_surveys_node(self, state: SurveyState) -> Dict[str, Any]:
        logger.info("Retrieving similar historical surveys for comparison")
        
        # Use the first image embedding as query (could be enhanced to combine multiple)
        if state["component_analyses"]:
            query_embedding = state["component_analyses"][0]["image_embedding"]
            
            # Get similar passing surveys for reference
            passing_surveys = await self.vector_store.search_similar_surveys(
                query_embedding, n_results=3, status_filter="pass"
            )
            
            # Get similar failing surveys for comparison
            failing_surveys = await self.vector_store.search_similar_surveys(
                query_embedding, n_results=2, status_filter="fail"
            )
            
            similar_surveys = {
                "passing_examples": passing_surveys,
                "failing_examples": failing_surveys
            }
        else:
            similar_surveys = {"passing_examples": [], "failing_examples": []}
        
        return {"similar_surveys": similar_surveys}
    
    async def generate_report_node(self, state: SurveyState) -> Dict[str, Any]:
        logger.info("Generating comprehensive survey report")
        
        # Compile all analysis data
        analyses = "\n\n".join([comp["analysis"] for comp in state["component_analyses"]])
        
        # Format similar survey context
        passing_context = ""
        if state["similar_surveys"]["passing_examples"]:
            passing_context = "\n".join([
                f"Similar passing survey: {survey['analysis']}"
                for survey in state["similar_surveys"]["passing_examples"][:2]
            ])
        
        failing_context = ""
        if state["similar_surveys"]["failing_examples"]:
            failing_context = "\n".join([
                f"Similar failing survey: {survey['analysis']}"
                for survey in state["similar_surveys"]["failing_examples"][:2]
            ])
        
        report_prompt = f"""
        Based on the component analysis and historical survey data, generate a comprehensive site survey report.
        
        CURRENT SURVEY ANALYSIS:
        {analyses}
        
        ADDITIONAL NOTES:
        {state.get('text_notes', 'None provided')}
        
        HISTORICAL CONTEXT - PASSING SURVEYS:
        {passing_context or 'No similar passing surveys found'}
        
        HISTORICAL CONTEXT - FAILING SURVEYS:
        {failing_context or 'No similar failing surveys found'}
        
        Generate a report that includes:
        1. Executive Summary (Pass/Fail determination)
        2. Component-by-Component Analysis
        3. Comparison to Historical Standards
        4. Specific Issues Found (if any)
        5. Recommendations
        6. Confidence Level
        
        Format as a professional inspection report.
        """
        
        report = await self.multimodal_model.analyze_image(
            state["images"][0],  # Use first image for context
            report_prompt
        )
        
        return {"final_report": report}
    
    async def validate_checklist_node(self, state: SurveyState) -> Dict[str, Any]:
        logger.info("Validating against inspection checklist")
        
        # Extract pass/fail determination and confidence from the report
        validation_prompt = f"""
        Based on this inspection report, provide:
        1. Overall status: "PASS" or "FAIL"
        2. Confidence score: 0.0 to 1.0
        3. Brief justification
        
        Report:
        {state['final_report']}
        
        Response format:
        STATUS: [PASS/FAIL]
        CONFIDENCE: [0.0-1.0]
        JUSTIFICATION: [brief explanation]
        """
        
        validation_result = await self.multimodal_model.analyze_image(
            state["images"][0],
            validation_prompt
        )
        
        # Parse the validation result (simplified parsing)
        overall_status = "fail"  # default to fail for safety
        confidence_score = 0.5
        
        if "STATUS: PASS" in validation_result.upper():
            overall_status = "pass"
        
        # Extract confidence score using regex
        try:
            conf_match = re.search(r"CONFIDENCE:\s*([0-9.]+)", validation_result)
            if conf_match:
                confidence_score = float(conf_match.group(1))
        except (ValueError, AttributeError):
            pass
        
        return {
            "overall_status": overall_status,
            "confidence_score": confidence_score
        }
    
    async def run_survey_analysis(
        self,
        images: List[Image.Image],
        text_notes: str = "",
        survey_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run the complete survey analysis workflow.
        
        Args:
            images: List of PIL Images to analyze
            text_notes: Optional text notes for additional context
            survey_id: Optional survey identifier, generated if not provided
            
        Returns:
            Complete analysis results with status, report, and confidence
        """
        if not self.workflow:
            await self.initialize()
        
        if not survey_id:
            survey_id = str(uuid.uuid4())
        
        initial_state = {
            "images": images,
            "text_notes": text_notes,
            "survey_id": survey_id,
            "component_analyses": [],
            "similar_surveys": [],
            "final_report": "",
            "overall_status": "fail",
            "confidence_score": 0.0
        }
        
        final_state = await self.workflow.ainvoke(initial_state)
        
        # Store results in vector database for future reference
        if final_state["component_analyses"]:
            await self.vector_store.add_survey_record(
                survey_id=survey_id,
                image_embeddings=final_state["component_analyses"][0]["image_embedding"],
                metadata={
                    "num_images": len(images),
                    "has_notes": bool(text_notes),
                    "confidence": final_state["confidence_score"]
                },
                analysis_result=final_state["final_report"],
                status=final_state["overall_status"]
            )
        
        return final_state