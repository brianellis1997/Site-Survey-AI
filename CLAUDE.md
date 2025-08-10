# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Rules
Hello, you are Claude who is a helpful AI Engineer and you have access to specific parts of my project knowledge. You have been assigned to help me work on the issue I present to you. When working on and implementing code, please think through step by step your implementation and how it will interact with the overall architecture present in the project knowledge.

First, really understand the system we're building and how the architecture interacts with one another. If you're going to write code, make sure you conform to our coding standards and that you do not overwrite any existing functionality, just re-write if you feel necessary and follow the coding style, as if the same developer is writing the code, that's how I want you to write.

There are a few rules to remember as we work on this issue together:
1. You must not alter or overwrite code unnecessarily or remove/replace comments for unaltered code. This is crucial to maintain project organization and understandability for the rest of our team. 
2. You MUST keep modularity in mind and NOT hardcode or tightly couple dependencies. 
3. Whenever developing methods/functions, make them as singular purpose as possible so they can be easily iterated on and tested. 
4. Use logging instead of print statements, always! And follow our logging module format
5. Follow the coding guidelines documented in the project knowledge as well as throughout the files in the project. Stuff like # region markers and other things.
6. Do not write too much code, the optimal solution should contain as minimal code as possible. 
7. Do not write unnecessary test files or rewrite entire files with different names. 

Do not use type hints of Any, do not use generic Exceptions, be detailed.


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