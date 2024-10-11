import os

from time import (
    sleep,
)

import uvicorn

import logging

from src.api import ports  # type: ignore
from src.app import app  # type: ignore

logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  
    handlers=[logging.StreamHandler()] 
)

log = logging.getLogger("hiq_image_captioner")

from fastapi.middleware.cors import (
    CORSMiddleware,
)
from fastapi.middleware.gzip import (
    GZipMiddleware,
)

from fastapi.staticfiles import (
    StaticFiles,
)

from .helpers.loaders import (
    ModuleLoader,
)


loader = ModuleLoader(ports)
names = loader.available_modules()
ACTIVE_PORTS = loader.load_modules(names)

openapi_tags = []
for port in ACTIVE_PORTS:
    if hasattr(
        port,
        "TAG",
    ):
        openapi_tags.append(
            {
                "name": port.TAG,
                "description": port.DESCRIPTION,
                "order": port.API_ORDER,
            }
        )

app.openapi_tags = openapi_tags

ACTIVE_PORTS.sort(
    key=lambda x: getattr(
        x,
        "API_ORDER",
        1000,
    ),
    reverse=True,
)


for port in ACTIVE_PORTS:
    prefix = "/".join(
        [
            "",
            "aiml",
            port.__name__.split(".")[-1],
        ]
    )
    app.include_router(
        port.router,
        prefix=prefix,
    )
    print(f"Activating: {port.__name__} with prefix: {prefix}")

app.add_middleware(
    GZipMiddleware,
    minimum_size=500,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


for path in loader.find(
    type_="d",
    name="static",
):
    name = os.path.basename(path)
    app.mount(
        f"/{name}",
        StaticFiles(directory=path),
        name=name,
    )
    break


@app.get("/")
async def root():
    return {"message": "Hello World!!"}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=14080,
        reload=True,
        reload_dirs=["/app"],
        reload_excludes=[".venv"],
        loop="uvloop",
    )
