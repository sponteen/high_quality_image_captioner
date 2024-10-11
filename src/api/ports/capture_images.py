from fastapi import (
    File,
    UploadFile,
    APIRouter,
    Depends,
)
from fastapi.responses import (
    JSONResponse,
)

from src.constants.hiq_images_endpoint import DESCRIPTION, TAG  # type: ignore
from src.helpers.generators import generate_captions  # type: ignore
from src.models.images import ImageMetadata  # type: ignore

from typing import (
    List,
)

API_ORDER = 0

router = APIRouter()


@router.post(
    "/hq/{user_uuid}",
    tags=[TAG],
    description=DESCRIPTION,
)
async def capture_hq_images(
    user_uuid: str,
    images: List[UploadFile] = File(...),
    metadata: List[ImageMetadata] = Depends(),
) -> JSONResponse:
    if len(images) != len(metadata):
        return JSONResponse(
            status_code=400,
            content={"error": "The number of images and metadata must be the same."},
        )

    image_orders = [metadata[index].image_order for index in range(len(images))]
    if len(set(image_orders)) != len(image_orders):
        return JSONResponse(
            status_code=400,
            content={"error": "The image orders must be unique."},
        )

    try:
        async for index, caption in enumerate(
            generate_captions(images, processor, model)  # type: ignore
        ):
            image_order = image_orders[index]
    except ValueError as e:
        log.error(f"Image corresponding to user {user_uuid} could not be processed: {str(e)}", exc_info=True) # type: ignore
        return JSONResponse(status_code=400, content={"error": "An error occurred while processing the image."})
    except Exception as e:
        log.critical(f"An error occurred while processing images for user {user_uuid}: {str(e)}", exc_info=True) # type: ignore
        return JSONResponse(status_code=500, content={"error": "An error occurred while processing images."})
