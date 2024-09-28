from fastapi import FastAPI

app = FastAPI(
    title="High Quality Image Captioner",
    description="""
    The high quality image captioner, used for Human User profile images, and small bathces of Human User images that were sent during a chat session.
    """,
    summary="High Quality Image Captioner",
    swagger_ui_parameters={
        "deepLinking": False,
        # "defaultModelRendering": "model",
        "operationsSorter": "alpha",
        "syntaxHighlight": True,
    },
    version="0.0.1",
)
