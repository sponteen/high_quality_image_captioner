from pydantic import (
    BaseModel, Field
)
from typing import (
    Literal
)

class ImageMetadata(BaseModel):
    image_order: Literal[
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
    ] = Field(
        description="The order of the image in the profile picture quadrant",
        examples=[3],
    )


"""
from typing import List
from typing_extensions import Self
from pydantic import PositiveFloat, model_validator
from syncmodels.model import BaseModel, Field


class ImageData(BaseModel):
    image_order: PositiveInt = Field(
        description="The order of the image in the profile picture quadrant",
        examples=[3],
    )
    image_bytes: bytes = Field(
        description="The image data in bytes, in the format of base64",
        examples=[
            b"iVBORw[................................................................]"
        ],
    )


class ImagesSequence(BaseModel):
    images_data: List[ImageData] = Field(
        description="A list of images data, i.e. image bytes and the image order in the sequence.",
    )
    user_uuid: str = Field(
        description="The UUID of the user to whom the sequence belongs to (UUID4)",
        examples=["8ae8f439-fd6b-46b8–9608–491d692da6d2"],
    )
"""
