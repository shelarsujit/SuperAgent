import os
from typing import Callable

from .model_registry import get_model_info

try:
    from transformers import pipeline
except Exception:  # pragma: no cover - optional dependency
    pipeline = None

from src.services.azure_client import call_azure


def load_model(task: str) -> Callable:
    """Return a callable for the given task.

    If an Azure endpoint is configured for this model, return a wrapper that
    calls the endpoint. Otherwise fall back to a local transformers pipeline.
    """
    model_info = get_model_info(task)

    # Azure endpoints are treated as full URLs
    if model_info.startswith("http"):
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")

        def call(payload: dict):
            return call_azure(model_info, api_key, payload)

        return call

    if pipeline is None:
        raise RuntimeError("transformers is required for local model loading")

    return pipeline(task, model=model_info)
