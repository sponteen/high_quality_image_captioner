import os
import asyncpg

from fastapi import (
    FastAPI,
)

from transformers import (
    BlipProcessor,
    BlipForConditionalGeneration,
)

from contextlib import asynccontextmanager

"""
async def get_database_pool():
    return await asyncpg.create_pool(
        user='postgres',                # Username for database authentication
        password='dev123',        # Password for database authentication
        database='your_database',        # Name of the database to connect to
        host='localhost',                # Database host (e.g., 'localhost' or IP address)
        port=5432,                       # Database port (default PostgreSQL port is 5432)
        min_size=1,                     # Minimum number of connections in the pool
        max_size=10,                    # Maximum number of connections in the pool
        timeout=60,                     # Maximum time (in seconds) to wait for a connection from the pool
        max_queries=50000,              # Maximum number of queries a connection can execute before being closed
        max_inactive_connection_lifetime=300,  # Time (in seconds) before a connection is closed if inactive
        command_timeout=60,             # Default timeout for database commands (in seconds)
        ssl=None,                       # SSL configuration, can be a dict or None
        prepare=False,                   # Whether to prepare statements (set to True to enable)
        server_settings=None,           # Custom server settings (like `application_name`)
    )
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
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
    )

    # database_pool = await get_database_pool()

    yield

    # await database_pool.close()


APP_DESCRIPTION = """
    The high quality image captioner, used for Human User profile images,
    and small batches of Human User images that were sent during a chat session. 
    """
app = FastAPI(
    title="High Quality Image Captioner",
    lifespan=lifespan,
    description=APP_DESCRIPTION,
    summary="High Quality Image Captioner",
    swagger_ui_parameters={
        "deepLinking": False,
        "operationsSorter": "alpha",
        "syntaxHighlight": True,
    },
    version="0.0.1",
)
