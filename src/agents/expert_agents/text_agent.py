from typing import Dict, Any
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from datetime import datetime
from langchain.llms import OpenAI, AzureOpenAI

try:  # Optional Gemini dependency
    import google.generativeai as genai
except Exception:  # pragma: no cover - optional
    genai = None

class TextAgent:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.model_name = model_name
        self.provider = "openai"

        gemini_key = os.environ.get("GEMINI_API_KEY")
        if gemini_key and genai is not None:
            try:
                genai.configure(api_key=gemini_key)
                model_name = os.environ.get("GEMINI_MODEL_NAME", "gemini-pro")
                self.gemini_model = genai.GenerativeModel(model_name)
                self.provider = "gemini"
            except Exception:  # pragma: no cover - missing dependency
                self.gemini_model = None

        if self.provider != "gemini":
            if os.environ.get("AZURE_OPENAI_ENDPOINT"):
                self.llm = AzureOpenAI(
                    deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", model_name),
                    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
                    azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
                )
                self.provider = "azure"
            else:
                self.llm = OpenAI(model_name=model_name)  # Local/OpenAI fallback
                self.provider = "openai"

        self.prompt_template = PromptTemplate(
            input_variables=["input_text"],
            template="You are a helpful text assistant. Respond to the following: {input_text}"
        )

        if self.provider != "gemini":
            self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
        else:
            self.chain = None

    def process(self, input_text: str) -> Dict[str, Any]:
        """
        Process the text input and generate a response.
        """
        if self.provider == "gemini" and self.gemini_model is not None:
            prompt = self.prompt_template.format(input_text=input_text)
            result = self.gemini_model.generate_content(prompt)
            response = result.text if hasattr(result, "text") else str(result)
        else:
            response = self.chain.run(input_text=input_text)
        return {
            "type": "text",
            "input": input_text,
            "output": response,
            "metadata": {
                "model": self.model_name,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
