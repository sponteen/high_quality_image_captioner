from io import BytesIO

from PIL import (
    Image,
)

from transformers import (
    BlipProcessor,
    BlipForConditionalGeneration,
)


def caption_image(image) -> str:
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
        image = Image.open(BytesIO(image_data))

        if (
            image.size[0] > MAX_DIMENSIONS_HIQ_IMAGE[0]
            or image.size[1] > MAX_DIMENSIONS_HIQ_IMAGE[1]
        ):
            image.thumbnail(size=MAX_DIMENSIONS_HIQ_IMAGE)

        caption = caption_image(image)

        yield caption
