import PyPDF2

class PDFProcessor:
    """Utility class to extract text from PDF documents."""

    @staticmethod
    def extract_text(file_path: str) -> str:
        text = ""
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        return text
