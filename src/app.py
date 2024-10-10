import os

from fastapi import (
    FastAPI,
)

from transformers import (
    BlipProcessor,
    BlipForConditionalGeneration,
)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs("./model_storage/blip_large/blip_large_processor", exist_ok=True)
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    processor.save_pretrained("./model_storage/blip_large/blip_large_processor", from_pt=True)

    os.makedirs("./model_storage/blip_large/blip_large_model", exist_ok=True)
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")
    model.save_pretrained("./model_storage/blip_large/blip_large_model", from_pt=True)
    
    processor = BlipProcessor.from_pretrained(
        "./model_storage/blip_large/blip_large_processor"
    )
    model = BlipForConditionalGeneration.from_pretrained(
        "./model_storage/blip_large/blip_large_model"
    )

    yield


    
APP_DESCRIPTION = """
    The high quality image captioner, used for Human User profile images,
    and small batches of Human User images that were sent during a chat session. 
    """
app = FastAPI(
    title="High Quality Image Captioner",
    lifespan=lifespan,
    description=APP_DESCRIPTION,
    summary="High Quality Image Captioner",
    swagger_ui_parameters={
        "deepLinking": False,
        "operationsSorter": "alpha",
        "syntaxHighlight": True,
    },
    version="0.0.1",
)
