import os

# Mapping of logical model tasks to either local model names or Azure deployment IDs
MODEL_REGISTRY = {
    "classification": os.environ.get("AZURE_CLASSIFY_DEPLOYMENT", "facebook/bart-large-mnli"),
    "summarization": os.environ.get("AZURE_SUMMARIZE_DEPLOYMENT", "sshleifer/distilbart-cnn-12-6"),
    "image_caption": os.environ.get("AZURE_IMAGE_DEPLOYMENT", "Salesforce/blip-image-captioning-base"),
}


def get_model_info(task: str) -> str:
    """Return the registered model or deployment name for a given task."""
    if task not in MODEL_REGISTRY:
        raise ValueError(f"No model registered for task: {task}")
    return MODEL_REGISTRY[task]
