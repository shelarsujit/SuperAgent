from typing import Literal, Dict, Any
from langgraph.graph import MessageGraph
from .expert_agents.text_agent import TextAgent
from .expert_agents.image_agent import ImageAgent
from .expert_agents.file_agent import FileAgent
from .expert_agents.link_agent import LinkAgent
import os
from src.services.azure_client import zero_shot_classify
from src.core.memory.short_term import ShortTermMemory
from src.core.memory.long_term import LongTermMemory
from src.services.cosmos_client import CosmosConversationLogger

try:
    from transformers import pipeline  # Fallback when Azure is not configured
except Exception:  # pragma: no cover - transformers may not be installed
    pipeline = None

class RouterAgent:
    def __init__(self, config: Dict[str, Any]):
        self.agents = {
            "text": TextAgent(),
            "image": ImageAgent(),
            "file": FileAgent(),
            "link": LinkAgent()
        }
        
        # Determine whether Azure endpoints are configured
        self.use_azure = bool(os.environ.get("AZURE_OPENAI_CLASSIFY_ENDPOINT"))
        if not self.use_azure and pipeline is not None:
            # Fallback to local transformers pipeline
            self.classifier = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli",
            )
        else:
            self.classifier = None
        
        # Memory components
        mem_cfg = config.get("memory", {}) if config else {}
        capacity = mem_cfg.get("short_capacity", 5)
        storage = mem_cfg.get("long_path", "long_term_memory.json")
        self.short_term = ShortTermMemory(capacity=capacity)
        self.long_term = LongTermMemory(storage_path=storage)

        # Optional Cosmos DB logging
        cosmos_cfg = config.get("cosmos", {}) if config else {}
        conn_str = os.environ.get("AZURE_COSMOS_CONNECTION_STRING")
        db_name = cosmos_cfg.get("database", os.environ.get("AZURE_COSMOS_DATABASE", "SuperAgent"))
        container_name = cosmos_cfg.get("container", os.environ.get("AZURE_COSMOS_CONTAINER", "conversations"))
        if conn_str:
            try:
                self.cosmos_logger = CosmosConversationLogger(conn_str, db_name, container_name)
            except Exception:  # pragma: no cover - optional dependency
                self.cosmos_logger = None
        else:
            self.cosmos_logger = None

        # Define the workflow graph
        self.workflow = MessageGraph()
        self._build_workflow()

        # Configure available labels for classification
        self.labels = ["text", "image", "file", "link"]

    def _classify_input(self, state: Dict[str, Any]) -> Literal["text", "image", "file", "link"]:
        """Classify input using Azure or local model."""
        if self.use_azure:
            return zero_shot_classify(state["input"], self.labels)
        elif self.classifier is not None:
            result = self.classifier(
                state["input"],
                candidate_labels=self.labels,
            )
            return result["labels"][0]
        else:
            return "text"

    def _route_input(self, state: Dict[str, Any]) -> Literal["text", "image", "file", "link"]:
        """Routing decision logic"""
        input_type = self._classify_input(state)
        print(f"Routing to {input_type} agent")
        return input_type

    def _build_workflow(self):
        """Construct the LangGraph workflow"""
        # Add nodes for each agent
        self.workflow.add_node("router", self._route_input)
        
        for agent_type in self.labels:
            if agent_type == "file":
                self.workflow.add_node(
                    agent_type,
                    lambda state, agent_type=agent_type: self.agents[agent_type].process(
                        state["input"], state.get("file_type", "")
                    ),
                )
            else:
                self.workflow.add_node(
                    agent_type,
                    lambda state, agent_type=agent_type: self.agents[agent_type].process(state["input"])
                )

        # Define edges
        self.workflow.add_edge("router", "text")
        self.workflow.add_edge("router", "image")
        self.workflow.add_edge("router", "file")
        self.workflow.add_edge("router", "link")
        
        # Set entry point
        self.workflow.set_entry_point("router")

    async def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point for processing requests"""
        try:
            # Add to workflow state
            state = {"input": input_data["content"]}
            conv_id = input_data.get("conversation_id", "default")
            if self.cosmos_logger:
                try:
                    self.cosmos_logger.log_message(conv_id, "user", input_data["content"])
                except Exception:
                    pass
            
            # Handle special cases for files/links
            if "metadata" in input_data:
                state.update(input_data["metadata"])
            
            # Execute the workflow
            results = await self.workflow.astream(state)
            
            # Collect and format results
            async for node_output in results:
                if node_output is not None:
                    text_in = str(input_data.get("content", ""))
                    text_out = (
                        node_output.get("output")
                        if isinstance(node_output, dict)
                        else str(node_output)
                    )
                    summary = await self.short_term.add_and_summarize(
                        f"{text_in} {text_out}"
                    )
                    self.long_term.add(summary)
                    if self.cosmos_logger:
                        try:
                            self.cosmos_logger.log_message(conv_id, "agent", text_out)
                        except Exception:
                            pass
                    return {
                        "status": "success",
                        "result": node_output,
                        "source": "agent"
                    }
                    
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

        return {
            "status": "error",
            "message": "No agent could process the input"
        }

# Example usage
if __name__ == "__main__":
    import asyncio

    async def run_tests():
        router = RouterAgent(config={})

        # Test different inputs
        test_cases = [
            {"content": "What is quantum computing?"},
            {"content": "https://example.com/image.jpg"},
            {"content": "document.pdf", "metadata": {"file_type": "pdf"}},
            {"content": "https://news.example.com/article"}
        ]

        for case in test_cases:
            response = await router.process_input(case)
            print(f"Input: {case['content']}")
            print(f"Response: {response}\n")

    asyncio.run(run_tests())
