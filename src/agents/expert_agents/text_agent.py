from typing import Dict, Any
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI  # or any other LLM

class TextAgent:
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        self.model_name = model_name
        self.llm = OpenAI(model_name=model_name)  # Initialize the LLM
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