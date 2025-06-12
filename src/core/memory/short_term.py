from collections import deque
from typing import Deque, List

from langgraph.graph import MessageGraph
from src.services.azure_client import summarize


class ShortTermMemory:
    """Conversation buffer with optional summarization."""

    def __init__(self, capacity: int = 5):
        self.buffer: Deque[str] = deque(maxlen=capacity)
        self.graph = MessageGraph()
        self.graph.add_node("add", self._add)
        self.graph.add_node("summarize", self._summarize)
        self.graph.add_edge("add", "summarize")
        self.graph.set_entry_point("add")

    def _add(self, message: str) -> str:
        self.buffer.append(message)
        return message

    def _summarize(self, _message: str) -> str:
        text = " ".join(self.buffer)
        try:
            return summarize(text)
        except Exception:
            return text

    async def add_and_summarize(self, message: str) -> str:
        async for result in self.graph.astream(message):
            return result

    def get_context(self) -> List[str]:
        return list(self.buffer)
