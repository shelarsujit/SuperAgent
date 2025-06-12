import types
import sys
import importlib
import pytest

# ----- Stub modules and classes -----
class DummyMessageGraph:
    def __init__(self):
        self.nodes = {}
        self.entry_point = None

    def add_node(self, name, func):
        self.nodes[name] = func

    def add_edge(self, frm, to):
        pass

    def set_entry_point(self, name):
        self.entry_point = name

    async def astream(self, state):
        router_func = self.nodes[self.entry_point]
        label = router_func(state)
        result = self.nodes[label](state)
        async def gen():
            yield result
        return gen()

class DummyTextAgent:
    def process(self, state):
        return {"handled_by": "text"}

class DummyImageAgent:
    def process(self, state):
        return {"handled_by": "image"}

class DummyFileAgent:
    def process(self, state):
        return {"handled_by": "file"}

class DummyLinkAgent:
    def process(self, state):
        return {"handled_by": "link"}

# Register stub modules before importing RouterAgent
langgraph_module = types.ModuleType("langgraph.graph")
langgraph_module.MessageGraph = DummyMessageGraph
sys.modules["langgraph.graph"] = langgraph_module

for name, cls in {
    "text_agent": DummyTextAgent,
    "image_agent": DummyImageAgent,
    "file_agent": DummyFileAgent,
    "link_agent": DummyLinkAgent,
}.items():
    mod = types.ModuleType(f"src.agents.expert_agents.{name}")
    # Expose the class with the expected name used by RouterAgent
    original_name = {
        DummyTextAgent: "TextAgent",
        DummyImageAgent: "ImageAgent",
        DummyFileAgent: "FileAgent",
        DummyLinkAgent: "LinkAgent",
    }[cls]
    mod.__dict__[original_name] = cls
    sys.modules[f"src.agents.expert_agents.{name}"] = mod

# Minimal transformers stub
class DummyClassifier:
    def __call__(self, text, candidate_labels):
        return {"labels": ["text"]}

def dummy_pipeline(*args, **kwargs):
    return DummyClassifier()

transformers_module = types.ModuleType("transformers")
transformers_module.pipeline = dummy_pipeline
sys.modules["transformers"] = transformers_module

# Import RouterAgent after stubs are in place
RouterAgent = importlib.import_module("src.agents.router_agent").RouterAgent

@pytest.mark.asyncio
async def test_process_input_routes_text():
    # Patch the workflow builder to avoid missing attributes
    def dummy_build_workflow(self):
        self.labels = ["text", "image", "file", "link"]
        self.workflow = DummyMessageGraph()
        self.workflow.add_node("router", self._route_input)
        for agent_type in self.labels:
            self.workflow.add_node(
                agent_type,
                lambda state, agent_type=agent_type: self.agents[agent_type].process(state)
            )
        self.workflow.set_entry_point("router")

    RouterAgent._build_workflow = dummy_build_workflow

    router = RouterAgent(config={})
    result = await router.process_input({"content": "hello"})
    assert result["status"] == "success"
    assert result["result"] == {"handled_by": "text"}

