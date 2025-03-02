from typing import Dict, Any
import PyPDF2
import pandas as pd
from io import StringIO

class FileAgent:
    def __init__(self):
        pass

    def process(self, file_path: str, file_type: str) -> Dict[str, Any]:
        """
        Process the file input based on its type.
        """
        if file_type == "pdf":
            return self._process_pdf(file_path)
        elif file_type == "csv":
            return self._process_csv(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def _process_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from a PDF file.
        """
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

        return {
            "type": "file",
            "input": file_path,
            "output": text,
            "metadata": {
                "file_type": "pdf",
                "timestamp": "2023-10-01T12:00:00Z"  # Add actual timestamp logic
            }
        }

    def _process_csv(self, file_path: str) -> Dict[str, Any]:
        """
        Extract data from a CSV file.
        """
        df = pd.read_csv(file_path)
        return {
            "type": "file",
            "input": file_path,
            "output": df.to_dict(),
            "metadata": {
                "file_type": "csv",
                "timestamp": "2023-10-01T12:00:00Z"  # Add actual timestamp logic
            }
        }