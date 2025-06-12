from typing import Dict, Any
import os
from src.services.azure_client import caption_image
from PIL import Image
import requests
from io import BytesIO
from transformers import BlipProcessor, BlipForConditionalGeneration

class ImageAgent:
    def __init__(self, model_name: str = "Salesforce/blip-image-captioning-base"):
        self.model_name = model_name
        self.use_azure = bool(os.environ.get("AZURE_IMAGE_CAPTION_ENDPOINT"))
        if not self.use_azure:
            self.processor = BlipProcessor.from_pretrained(model_name)
            self.model = BlipForConditionalGeneration.from_pretrained(model_name)

    def process(self, image_url: str) -> Dict[str, Any]:
        """
        Process the image input and generate a caption or description.
        """
        if self.use_azure:
            caption = caption_image(image_url)
        else:
            # Load image from URL
            response = requests.get(image_url)
            image = Image.open(BytesIO(response.content)).convert("RGB")

            # Generate caption locally
            inputs = self.processor(image, return_tensors="pt")
            out = self.model.generate(**inputs)
            caption = self.processor.decode(out[0], skip_special_tokens=True)

        return {
            "type": "image",
            "input": image_url,
            "output": caption,
            "metadata": {
                "model": self.model_name,
                "timestamp": "2023-10-01T12:00:00Z"  # Add actual timestamp logic
            }
        }