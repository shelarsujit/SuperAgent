from typing import Literal, Dict, Any
from langgraph.graph import MessageGraph
from .expert_agents.text_agent import TextAgent
from .expert_agents.image_agent import ImageAgent
from .expert_agents.file_agent import FileAgent
from .expert_agents.link_agent import LinkAgent
from transformers import pipeline  # For input classification

class RouterAgent:
    def __init__(self, config: Dict[str, Any]):
        self.agents = {
            "text": TextAgent(),
            "image": ImageAgent(),
            "file": FileAgent(),
            "link": LinkAgent()
        }
        
        # Initialize classifier for input routing
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        
        # Define the workflow graph
        self.workflow = MessageGraph()
        self._build_workflow()
        
        # Configure available labels for classification
        self.labels = ["text", "image", "file", "link"]

    def _classify_input(self, state: Dict[str, Any]) -> Literal["text", "image", "file", "link"]:
        """Classify input using zero-shot classification"""
        result = self.classifier(
            state["input"],
            candidate_labels=self.labels
        )
        return result["labels"][0]  # Return top predicted label

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
            self.workflow.add_node(
                agent_type,
                lambda state, agent_type=agent_type: self.agents[agent_type].process(state)
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
            
            # Handle special cases for files/links
            if "metadata" in input_data:
                state.update(input_data["metadata"])
            
            # Execute the workflow
            results = await self.workflow.astream(state)
            
            # Collect and format results
            async for node_output in results:
                if node_output is not None:
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
    router = RouterAgent(config={})
    
    # Test different inputs
    test_cases = [
        {"content": "What is quantum computing?"},
        {"content": "https://example.com/image.jpg"},
        {"content": "document.pdf", "metadata": {"file_type": "pdf"}},
        {"content": "https://news.example.com/article"}
    ]
    
    for case in test_cases:
        response = router.process_input(case)
        print(f"Input: {case['content']}")
        print(f"Response: {response}\n")