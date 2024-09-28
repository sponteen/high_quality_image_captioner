"""Main aiml module.

Contains the FastAPI REST component
"""

import os


from time import sleep


import uvicorn

from .cli import main

import logging

log = logging.getLogger(__name__)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .helpers.loaders import ModuleLoader
from src.api import ports

from src.app import app

loader = ModuleLoader(ports)
names = loader.available_modules()
ACTIVE_PORTS = loader.load_modules(names)

openapi_tags = []
for port in ACTIVE_PORTS:
    if hasattr(port, "TAG"):
        openapi_tags.append(
            {
                "name": port.TAG,
                "description": port.DESCRIPTION,
                "order": port.API_ORDER,
            }
        )

app.openapi_tags = openapi_tags

ACTIVE_PORTS.sort(key=lambda x: getattr(x, "API_ORDER", 1000), reverse=True)

# ---------------------------------------------------------
# Create FastAPI application
# ---------------------------------------------------------


# ---------------------------------------------------------
# user specific EPs (1st Ports)
# ---------------------------------------------------------
# TODO: fix appearance order in Swagger documentation

for port in ACTIVE_PORTS:
    prefix = "/".join(["", "aiml", port.__name__.split(".")[-1]])
    app.include_router(port.router, prefix=prefix)
    print(f"Activating: {port.__name__} with prefix: {prefix}")

# old router adding fashion
# app.include_router(search.router)
# app.include_router(stats.router)
# app.include_router(config.router)

# ---------------------------------------------------------
# Middleware settings
# ---------------------------------------------------------
app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO def for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# ---------------------------------------------------------
# Static assets
# ---------------------------------------------------------
for path in loader.find(type_="d", name="static"):
    name = os.path.basename(path)
    app.mount(f"/{name}", StaticFiles(directory=path), name=name)
    break


# ---------------------------------------------------------
# heartbeat EP
# ---------------------------------------------------------
@app.get("/")
async def root():
    return {"message": "Hello World!!"}


# ---------------------------------------------------------
# direct execution case (python -m xxxx)
# (not used by now)
# ---------------------------------------------------------
if __name__ == "__main__":
    """
    $ uvicorn aiml.aiml:app --reload --reload-delay 1 --reload-dir ~/your/code/aiml --reload-exclude '.venv' --loop uvloop
    """

    uvicorn.run(app, host="0.0.0.0", port=14080)
