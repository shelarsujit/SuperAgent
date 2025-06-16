# SuperAgent

An intelligent agent routing system with multi-modal capabilities.

## Features
- Multi-model routing core
- File/image/link processing
- Short & long-term memory
- External knowledge integration
- Web UI & API access

## Quick Start
```bash
git clone https://github.com/yourusername/SuperAgent.git
cd SuperAgent
pip install -r requirements.txt

# Configure Azure endpoints
export AZURE_OPENAI_API_KEY=<your-key>
export AZURE_OPENAI_ENDPOINT=<https://your-resource.openai.azure.com>
export AZURE_OPENAI_DEPLOYMENT_NAME=<deployment>

# (Optional) Configure Google Gemini
export GEMINI_API_KEY=<your-gemini-key>
export GEMINI_MODEL_NAME=gemini-pro

# Start the API
uvicorn src.services.api.fastapi_app.main:app --reload
```

## Orchestration
The project uses Azure-hosted models when the corresponding environment variables are set. If `GEMINI_API_KEY` is provided, text requests will be routed to Google's Gemini model instead. Deploy your models to Azure OpenAI or Azure Cognitive Services and provide the deployment names or endpoint URLs as environment variables such as `AZURE_CLASSIFY_DEPLOYMENT` or `AZURE_VECTOR_ENDPOINT`.

## Agentic Core
LangGraph is used throughout the `core` modules to manage short- and long-term memory as well as high level planning. These graphs can call Azure endpoints for tasks like summarization or classification, allowing flexible orchestration across services.

## Frontend Usage
The `frontend/` directory contains a minimal WebSocket chat interface. After starting the API server you can serve the static files using Python's built in HTTP server:

```bash
# from the repository root
python -m http.server --directory frontend 8080
```

Then open `http://localhost:8080` in your browser. The page lets you send text messages over the WebSocket and upload files through the `/upload` endpoint.
