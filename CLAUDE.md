# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Site Survey AI is a multimodal AI system for automated manufacturing equipment inspection. It uses open-source vision-language models (Gemma/Qwen) from HuggingFace with ChromaDB vector storage and LangGraph workflows to analyze equipment images and generate inspection reports.

## Development Commands

### Environment Setup
```bash
python setup.py                    # Initial environment setup and dependency installation
source survey-env/bin/activate     # Activate virtual environment (Linux/Mac)
survey-env\Scripts\activate        # Activate virtual environment (Windows)
```

### Running the Application
```bash
python main.py                     # Start FastAPI server on localhost:8000
python example_usage.py            # Run example usage scenarios
```

### Configuration
- Copy `.env.example` to `.env` and configure settings
- Key settings: `MODEL_NAME`, `API_PORT`, `CHROMA_DB_PATH`, `LOG_LEVEL`

## Architecture Overview

The system follows an agentic workflow pattern using LangGraph:

### Core Components
- **FastAPI API** (`src/site_survey_ai/api/main.py`): REST endpoints for survey analysis
- **LangGraph Workflow** (`src/site_survey_ai/agents/survey_workflow.py`): 5-step analysis pipeline
- **Vector Store** (`src/site_survey_ai/database/vector_store.py`): ChromaDB for RAG similarity search
- **Multimodal Model** (`src/site_survey_ai/models/multimodal_model.py`): HuggingFace vision-language models
- **Image Processor** (`src/site_survey_ai/utils/image_processor.py`): Preprocessing and embedding extraction

### Analysis Workflow
1. **process_images**: Preprocess uploaded images for analysis
2. **analyze_components**: Component-level analysis using multimodal AI
3. **retrieve_similar**: RAG-based search for similar historical surveys
4. **generate_report**: Comprehensive report generation with historical context
5. **validate_checklist**: Pass/fail determination with confidence scoring

### API Endpoints
- `POST /analyze-survey`: Upload images and notes for analysis
- `GET /survey/{survey_id}`: Retrieve previous survey results
- `GET /similar-surveys/{survey_id}`: Find similar surveys by embeddings
- `GET /stats`: Database statistics
- `GET /`: Health check

## Key Dependencies

- **torch/transformers**: Multimodal AI models (PaLiGemma, Kosmos-2)
- **langgraph/langchain**: Agentic workflow orchestration  
- **chromadb**: Vector database for similarity search
- **fastapi/uvicorn**: Web API framework
- **PIL/opencv**: Image processing
- **open-clip-torch**: CLIP embeddings (replaces clip-by-openai for PyTorch compatibility)

## Development Notes

- Models are downloaded to `./models/` directory on first use
- ChromaDB stores embeddings in `./chroma_db/` directory
- All analysis results are stored in vector database for future RAG retrieval
- Default model: `google/paligemma-3b-pt-224` (configurable via .env)
- API runs with hot reload enabled for development

## Testing

Use `example_usage.py` for testing both direct component usage and API integration. The script creates synthetic equipment images for testing when no real survey images are available.