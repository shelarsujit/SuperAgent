import requests
from bs4 import BeautifulSoup


def fetch_url_text(url: str) -> str:
    """Retrieve the visible text from a web page."""
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    return " ".join(soup.stripped_strings)
