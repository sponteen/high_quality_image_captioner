from pydantic import BaseModel, Field, validator
from typing import Literal


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

    image_hash: str = Field(
        description="SHA1 hash of the image",
        example="a94a8fe5ccb19ba61c4c0873d391e987982fbbd3",
    )

    @validator("image_hash")
    def validate_hash(cls, value):
        if len(value) != 40:
            raise ValueError("The SHA1 hash must be exactly 40 characters long.")
        return value
