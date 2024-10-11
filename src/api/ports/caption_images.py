from contextlib import asynccontextmanager
import json
import os
import re
import logging

from fastapi import File, UploadFile, APIRouter, Form, FastAPI

from fastapi.responses import (
    JSONResponse,
)

import torch
from transformers import (
    BlipProcessor,
    BlipForConditionalGeneration,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

log = logging.getLogger("hiq_image_captioner")

from src.constants.hiq_images_endpoint import DESCRIPTION, TAG  # type: ignore
from src.helpers.generators import generate_captions  # type: ignore
from src.models.images import ImageMetadata  # type: ignore

from typing import (
    List,
)

API_ORDER = 0

processor = None
model = None
HEXA_DIGEST_32_BYTES_REGEXP = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    device = "cuda" if torch.cuda.is_available() else "cpu"

    os.makedirs("./model_storage/blip_large/blip_large_processor", exist_ok=True)
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    processor.save_pretrained(
        "./model_storage/blip_large/blip_large_processor", from_pt=True
    )
    processor = BlipProcessor.from_pretrained(
        "./model_storage/blip_large/blip_large_processor"
    )

    os.makedirs("./model_storage/blip_large/blip_large_model", exist_ok=True)
    model = BlipForConditionalGeneration.from_pretrained(
        "Salesforce/blip-image-captioning-large"
    )
    model.save_pretrained("./model_storage/blip_large/blip_large_model", from_pt=True)
    model = BlipForConditionalGeneration.from_pretrained(
        "./model_storage/blip_large/blip_large_model"
    ).to(device)

    HEXA_DIGEST_32_BYTES_REGEXP = re.compile(r"^[a-fA-F0-9]{64}$")

    # database_pool = await get_database_pool()

    yield

    # await database_pool.close()


router = APIRouter(lifespan=lifespan)


@router.post(
    "/hq/{user_uuid}",
    tags=[TAG],
    description=DESCRIPTION,
)
async def caption_hq_images(
    user_uuid: str,
    metadata: str = Form(...),
    images: List[UploadFile] = File(...),
) -> JSONResponse:
    metadata = [ImageMetadata(**item) for item in json.loads(metadata)]

    if not HEXA_DIGEST_32_BYTES_REGEXP.match(user_uuid):
        log.error(f"Invalid user UUID: {user_uuid} is not SHA256!")
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid user UUID. Check logs for more details."},
        )

    if len(images) != len(metadata):
        log.error(
            f"Inconsistancy between number of images [{len(images)}] and metadata [{len(metadata)}]!",
        )
        return JSONResponse(
            status_code=400,
            content={
                "error": "Inconsistancy in images and their metadata. Check logs for more details."
            },
        )

    image_orders = [metadata[index].image_order for index in range(len(images))]
    if len(set(image_orders)) != len(image_orders):
        log.error(
            f"Inconsistancy between number of images [{len(images)}] and metadata [{len(metadata)}]!",
        )
        return JSONResponse(
            status_code=409,
            content={"error": "The image orders are invalid!"},
        )

    images_with_orders = zip(image_orders, images)
    try:
        captions = []
        async for image_order, caption in generate_captions(
            images_with_orders, processor, model, device # type: ignore
        ):
            captions.append({"image_order": image_order, "caption": caption})
        return JSONResponse(status_code=200, content={"captions": captions})
    except ValueError as e:
        log.error(
            f"Image corresponding to user {user_uuid} could not be processed: {str(e)}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=400,
            content={"error": "An error occurred while processing the image."},
        )
    except Exception as e:
        log.critical(
            f"An error occurred while processing images for user {user_uuid}: {str(e)}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={"error": "An error occurred while processing images."},
        )
