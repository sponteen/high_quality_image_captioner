from io import BytesIO
from os import cpu_count
import torch
import psutil
from PIL import (
    Image,
)

from src.constants.hiq_images import MAX_DIMENSIONS_HIQ_IMAGE  # type: ignore

torch.set_num_threads(psutil.cpu_count(logical=True))


def caption_image(image, processor, model) -> str:
    inputs = processor(image, return_tensors="pt")

    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_length=100,
            min_length=60,
            num_beams=5,
            early_stopping=True,
            no_repeat_ngram_size=7
        )

    return processor.decode(output[0], skip_special_tokens=True)


async def generate_captions(images_with_orders, processor, model):
    model.eval()

    for order, image in images_with_orders:
        image = await image.read()
        image = Image.open(BytesIO(image)).convert("RGB")

        if (
            image.size[0] > MAX_DIMENSIONS_HIQ_IMAGE[0]
            or image.size[1] > MAX_DIMENSIONS_HIQ_IMAGE[1]
        ):
            raise ValueError("Profile image dimensions must be of 640x800 pixels.")

        caption = caption_image(image, processor, model)

        yield order, caption
