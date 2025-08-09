# 🔍 Site Survey AI

An intelligent multimodal AI system for automated site surveys and equipment inspection. This application analyzes images from manufacturing equipment, rockets, and other industrial components, comparing them against a knowledge base of historical surveys to automatically generate inspection reports.

## ✨ Features

- **🤖 Multimodal AI Analysis**: Uses open-source models (Gemma/Qwen) from HuggingFace for vision-language understanding
- **📊 RAG-Powered Comparisons**: ChromaDB vector store for retrieving similar historical surveys
- **🔄 Agentic Workflows**: LangGraph-based workflow system for structured analysis
- **📱 REST API**: FastAPI backend ready for mobile app integration  
- **🎯 Automated Reports**: Generate pass/fail inspection reports with confidence scores
- **🔍 Component Detection**: Basic computer vision for identifying equipment components
- **📈 Historical Tracking**: Store and analyze inspection trends over time

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mobile App    │────│   FastAPI       │────│  LangGraph      │
│   (Future)      │    │   Backend       │    │  Workflow       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   ChromaDB      │    │  HuggingFace    │
                       │ Vector Store    │    │   Models        │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- 4GB+ RAM (8GB+ recommended for local models)
- CUDA-compatible GPU (optional, but recommended)

### Installation

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd Site-Survey-AI
   python setup.py
   ```

2. **Activate environment**:
   ```bash
   source survey-env/bin/activate  # Linux/Mac
   # or
   survey-env\Scripts\activate     # Windows
   ```

3. **Configure settings**:
   ```bash
   cp .env.example .env
   # Edit .env with your preferred model and settings
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

5. **Test the system**:
   ```bash
   python example_usage.py
   ```

## 📡 API Usage

Once running, the API will be available at `http://localhost:8000`

### Analyze Survey
```bash
curl -X POST 'http://localhost:8000/analyze-survey' \
  -F 'images=@equipment1.jpg' \
  -F 'images=@equipment2.jpg' \
  -F 'notes=Routine inspection - check for wear and alignment'
```

### Get Survey Results
```bash
curl http://localhost:8000/survey/{survey_id}
```

### Find Similar Surveys
```bash
curl http://localhost:8000/similar-surveys/{survey_id}?limit=5&status_filter=pass
```

## 🛠️ Project Structure

```
src/site_survey_ai/
├── agents/           # LangGraph workflow definitions
├── api/             # FastAPI application
├── database/        # ChromaDB vector store
├── models/          # Multimodal AI model wrappers
└── utils/           # Image processing utilities
```

## 🔧 Configuration

Key settings in `.env`:

```env
# Model Configuration
MODEL_NAME=google/paligemma-3b-pt-224  # or microsoft/kosmos-2-patch14-224
MODEL_CACHE_DIR=./models

# Database
CHROMA_DB_PATH=./chroma_db

# API
API_HOST=0.0.0.0
API_PORT=8000
```

## 🎯 Workflow Process

1. **Image Processing**: Enhance contrast, resize, detect components
2. **Component Analysis**: Use multimodal AI to analyze each component
3. **Historical Comparison**: RAG search for similar past surveys
4. **Report Generation**: Create structured inspection report
5. **Validation**: Determine pass/fail status with confidence score

## 📊 Example Output

```json
{
  "survey_id": "uuid-123",
  "status": "pass",
  "confidence_score": 0.87,
  "report": "Inspection Summary: All critical components within acceptable parameters...",
  "num_images_processed": 3,
  "similar_surveys_found": {
    "passing": 5,
    "failing": 2
  }
}
```

## 🔮 Roadmap

- [ ] Mobile app frontend (React Native/Flutter)
- [ ] Model fine-tuning capabilities
- [ ] Advanced component detection
- [ ] Real-time streaming analysis
- [ ] Multi-tenant support
- [ ] Integration with external inspection databases
- [ ] Custom checklist templates

## 🤝 Contributing

This is an early-stage project. Contributions welcome for:
- Model optimization
- Mobile app development  
- Additional computer vision features
- Performance improvements

## 📄 License

[Add your license here]
