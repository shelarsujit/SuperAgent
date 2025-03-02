from typing import Dict, Any
import requests
from bs4 import BeautifulSoup

class LinkAgent:
    def __init__(self):
        pass

    def process(self, url: str) -> Dict[str, Any]:
        """
        Process the link and extract relevant information.
        """
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        # Extract title and first paragraph
        title = soup.title.string if soup.title else "No Title"
        first_paragraph = soup.find("p").get_text() if soup.find("p") else "No Content"

        return {
            "type": "link",
            "input": url,
            "output": {
                "title": title,
                "content": first_paragraph
            },
            "metadata": {
                "source": url,
                "timestamp": "2023-10-01T12:00:00Z"  # Add actual timestamp logic
            }
        }