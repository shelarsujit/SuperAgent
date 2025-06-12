from typing import Dict, Any
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from langchain.llms import OpenAI, AzureOpenAI

class TextAgent:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.model_name = model_name
        if os.environ.get("AZURE_OPENAI_ENDPOINT"):
            self.llm = AzureOpenAI(
                deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME", model_name),
                api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
                azure_endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            )
        else:
            self.llm = OpenAI(model_name=model_name)  # Local/OpenAI fallback
        self.prompt_template = PromptTemplate(
            input_variables=["input_text"],
            template="You are a helpful text assistant. Respond to the following: {input_text}"
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt_template)

    def process(self, input_text: str) -> Dict[str, Any]:
        """
        Process the text input and generate a response.
        """
        response = self.chain.run(input_text=input_text)
        return {
            "type": "text",
            "input": input_text,
            "output": response,
            "metadata": {
                "model": self.model_name,
                "timestamp": "2023-10-01T12:00:00Z"  # Add actual timestamp logic
            }
        }