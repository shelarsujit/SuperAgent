from __future__ import annotations
import os
from typing import List

from src.services.azure_client import call_azure


class VectorDB:
    """Very small in-memory vector store with optional Azure search."""

    def __init__(self):
        self.vectors: List[List[float]] = []
        self.texts: List[str] = []
        self.azure_endpoint = os.environ.get("AZURE_VECTOR_ENDPOINT")
        self.azure_key = os.environ.get("AZURE_COGNITIVE_KEY")

    def add(self, embedding: List[float], text: str) -> None:
        if self.azure_endpoint and self.azure_key:
            call_azure(self.azure_endpoint + "/add", self.azure_key, {"vec": embedding, "text": text})
        else:
            self.vectors.append(embedding)
            self.texts.append(text)

    def search(self, embedding: List[float], top_k: int = 1) -> List[str]:
        if self.azure_endpoint and self.azure_key:
            result = call_azure(self.azure_endpoint + "/search", self.azure_key, {"vec": embedding, "k": top_k})
            return result.get("texts", [])

        if not self.vectors:
            return []

        # naive dot-product search
        scores = [sum(e * q for e, q in zip(vec, embedding)) for vec in self.vectors]
        best_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [self.texts[i] for i in best_indices]
