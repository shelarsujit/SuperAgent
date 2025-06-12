import os
import requests


def call_azure(endpoint: str, api_key: str, payload: dict) -> dict:
    """Generic helper to POST JSON payloads to an Azure endpoint."""
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
    }
    response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()


def zero_shot_classify(text: str, labels: list[str]) -> str:
    """Classify text using an Azure OpenAI custom endpoint."""
    endpoint = os.environ.get("AZURE_OPENAI_CLASSIFY_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    if not endpoint or not api_key:
        raise RuntimeError("Azure OpenAI classification endpoint not configured")
    payload = {"text": text, "labels": labels}
    result = call_azure(endpoint, api_key, payload)
    return result.get("label", labels[0])


def summarize(text: str, max_length: int = 130, min_length: int = 30) -> str:
    """Summarize text via an Azure OpenAI endpoint."""
    endpoint = os.environ.get("AZURE_OPENAI_SUMMARIZE_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    if not endpoint or not api_key:
        raise RuntimeError("Azure OpenAI summarization endpoint not configured")
    payload = {
        "text": text,
        "max_length": max_length,
        "min_length": min_length,
    }
    result = call_azure(endpoint, api_key, payload)
    return result.get("summary", "")


def caption_image(image_url: str) -> str:
    """Generate an image caption using Azure Cognitive Services."""
    endpoint = os.environ.get("AZURE_IMAGE_CAPTION_ENDPOINT")
    api_key = os.environ.get("AZURE_COGNITIVE_KEY")
    if not endpoint or not api_key:
        raise RuntimeError("Azure image caption endpoint not configured")
    payload = {"image_url": image_url}
    result = call_azure(endpoint, api_key, payload)
    return result.get("caption", "")
