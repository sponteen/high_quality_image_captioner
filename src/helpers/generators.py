from io import BytesIO
import torch
from PIL import (
    Image,
)

from constants.hiq_images import MAX_DIMENSIONS_HIQ_IMAGE

def caption_image(image, processor, model) -> str:
    inputs = processor(image, return_tensors="pt")

    with torch.no_grad():
        output = model.generate( 
            **inputs,
            max_length=140,
            num_beams=5,
        )

    return processor.decode(output[0], skip_special_tokens=True) 


async def generate_captions(images, processor, model):
    model.eval()

    for image in images:
        image = await image.read()
        image = Image.open(BytesIO(image))

        if (
            image.size[0] > MAX_DIMENSIONS_HIQ_IMAGE[0]
            or image.size[1] > MAX_DIMENSIONS_HIQ_IMAGE[1]
        ):
            raise ValueError("Profile image dimensions must be of 640x800 pixels.")

        caption = caption_image(image, processor, model)    

        yield caption
