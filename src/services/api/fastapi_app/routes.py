from fastapi import APIRouter, UploadFile, File
from typing import Dict, Any
import os
import shutil

from src.agents.router_agent import RouterAgent

router = APIRouter()
router_agent = RouterAgent(config={})

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/health")
async def health() -> Dict[str, str]:
    """Simple health check."""
    return {"status": "ok"}

@router.post("/process")
async def process_input(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process arbitrary JSON input through the RouterAgent."""
    return await router_agent.process_input(data)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload a file and process it based on its type."""
    file_ext = os.path.splitext(file.filename)[1].lstrip(".").lower()
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    input_data = {
        "content": file_path,
        "metadata": {"file_type": file_ext},
    }
    return await router_agent.process_input(input_data)
