from transformers import pipeline

class TextProcessor:
    """Utility class for text-based processing tasks."""

    def __init__(self, model_name: str = "sshleifer/distilbart-cnn-12-6"):
        self.summarizer = pipeline("summarization", model=model_name)

    def summarize(self, text: str, max_length: int = 130, min_length: int = 30) -> str:
        """Return a summarized version of the provided text."""
        summary = self.summarizer(text, max_length=max_length, min_length=min_length)
        return summary[0]["summary_text"]
