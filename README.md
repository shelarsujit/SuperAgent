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

# Start the API
uvicorn src.services.api.fastapi_app.main:app --reload
```
