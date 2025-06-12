from typing import List

from langgraph.graph import MessageGraph
from src.services.azure_client import zero_shot_classify


class TaskDecomposer:
    """Break a high level goal into coarse tasks."""

    def __init__(self):
        self.graph = MessageGraph()
        self.graph.add_node("plan", self._plan)
        self.graph.set_entry_point("plan")
        self.labels = ["search_web", "analyze_file", "respond"]

    def _plan(self, goal: str) -> List[str]:
        label = zero_shot_classify(goal, self.labels)
        return [label]

    async def decompose(self, goal: str) -> List[str]:
        async for result in self.graph.astream(goal):
            return result
