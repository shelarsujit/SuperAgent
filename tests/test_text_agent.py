import importlib
import os
import sys
import types
from pathlib import Path

google_pkg = types.ModuleType('google')
genai = types.ModuleType('google.generativeai')
class DummyResponse:
    def __init__(self, text):
        self.text = text
class DummyModel:
    def __init__(self, name):
        self.name = name
    def generate_content(self, prompt):
        return DummyResponse(f"gemini:{prompt}")

def configure(api_key):
    pass

genai.configure = configure
genai.GenerativeModel = DummyModel
google_pkg.generativeai = genai
sys.modules['google'] = google_pkg
sys.modules['google.generativeai'] = genai

# Ensure the src directory is on the path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Stub minimal langchain modules so TextAgent can be imported without the real dependency
chains_mod = types.ModuleType('langchain.chains')
class DummyLLMChain:
    def __init__(self, llm=None, prompt=None):
        self.llm = llm
        self.prompt = prompt
    def run(self, input_text=""):
        return f"{input_text}"
chains_mod.LLMChain = DummyLLMChain
sys.modules['langchain.chains'] = chains_mod

prompts_mod = types.ModuleType('langchain.prompts')
class DummyPromptTemplate:
    def __init__(self, input_variables=None, template=""):
        self.template = template
    def format(self, **kwargs):
        return self.template.format(**kwargs)
prompts_mod.PromptTemplate = DummyPromptTemplate
sys.modules['langchain.prompts'] = prompts_mod

llms_mod = types.ModuleType('langchain.llms')
class DummyLLM:
    def __init__(self, *_, **__):
        pass
llms_mod.OpenAI = DummyLLM
llms_mod.AzureOpenAI = DummyLLM
sys.modules['langchain.llms'] = llms_mod
langchain_pkg = types.ModuleType('langchain')
langchain_pkg.chains = chains_mod
langchain_pkg.prompts = prompts_mod
langchain_pkg.llms = llms_mod
sys.modules['langchain'] = langchain_pkg

os.environ['GEMINI_API_KEY'] = 'x'
spec = importlib.util.spec_from_file_location(
    'src.agents.expert_agents.text_agent',
    Path(__file__).resolve().parents[1] / 'src/agents/expert_agents/text_agent.py'
)
ta = importlib.util.module_from_spec(spec)
sys.modules['src.agents.expert_agents.text_agent'] = ta
spec.loader.exec_module(ta)

def test_gemini_selection():
    agent = ta.TextAgent()
    result = agent.process("hi")
    assert result['output'].startswith('gemini:')
    assert agent.provider == 'gemini'


