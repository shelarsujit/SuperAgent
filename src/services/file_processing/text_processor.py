import os
from src.services.azure_client import summarize
try:
    from transformers import pipeline
except Exception:  # pragma: no cover - transformers optional
    pipeline = None

class TextProcessor:
    """Utility class for text-based processing tasks."""

    def __init__(self, model_name: str = "sshleifer/distilbart-cnn-12-6"):
        self.use_azure = bool(os.environ.get("AZURE_OPENAI_SUMMARIZE_ENDPOINT"))
        if not self.use_azure and pipeline is not None:
            self.summarizer = pipeline("summarization", model=model_name)
        else:
            self.summarizer = None

    def summarize(self, text: str, max_length: int = 130, min_length: int = 30) -> str:
        """Return a summarized version of the provided text."""
        if self.use_azure:
            return summarize(text, max_length=max_length, min_length=min_length)
        elif self.summarizer is not None:
            summary = self.summarizer(text, max_length=max_length, min_length=min_length)
            return summary[0]["summary_text"]
        else:
            return text
