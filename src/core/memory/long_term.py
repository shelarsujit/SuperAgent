import os
import json
from typing import List, Dict

from src.services.azure_client import call_azure


class LongTermMemory:
    """Persist messages locally or via Azure."""

    def __init__(self, storage_path: str = "long_term_memory.json"):
        self.storage_path = storage_path
        self.azure_endpoint = os.environ.get("AZURE_LONGTERM_ENDPOINT")
        self.azure_key = os.environ.get("AZURE_COGNITIVE_KEY")
        self.records: List[Dict[str, str]] = []
        if os.path.exists(storage_path):
            with open(storage_path, "r") as f:
                for line in f:
                    self.records.append(json.loads(line))

    def add(self, message: str) -> None:
        record = {"message": message}
        if self.azure_endpoint and self.azure_key:
            call_azure(self.azure_endpoint, self.azure_key, record)
        else:
            self.records.append(record)
            with open(self.storage_path, "a") as f:
                f.write(json.dumps(record) + "\n")

    def get_all(self) -> List[str]:
        return [r["message"] for r in self.records]
