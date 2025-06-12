from typing import Optional
import os
from PIL import Image
import requests
from io import BytesIO
from transformers import BlipProcessor, BlipForConditionalGeneration
from src.services.azure_client import caption_image

class ImageProcessor:
    """Perform basic image processing like caption generation."""

    def __init__(self, model_name: str = "Salesforce/blip-image-captioning-base"):
        self.use_azure = bool(os.environ.get("AZURE_IMAGE_CAPTION_ENDPOINT"))
        if not self.use_azure:
            self.processor = BlipProcessor.from_pretrained(model_name)
            self.model = BlipForConditionalGeneration.from_pretrained(model_name)

    def caption(self, image_url: str) -> str:
        if self.use_azure:
            return caption_image(image_url)
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content)).convert("RGB")
        inputs = self.processor(image, return_tensors="pt")
        out = self.model.generate(**inputs)
        return self.processor.decode(out[0], skip_special_tokens=True)
