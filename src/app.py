from fastapi import (
    FastAPI,
)


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


APP_DESCRIPTION = """
    The high quality image captioner, used for Human User profile images,
    and small batches of Human User images that were sent during a chat session. 
    """
app = FastAPI(
    title="High Quality Image Captioner",
    description=APP_DESCRIPTION,
    summary="High Quality Image Captioner",
    swagger_ui_parameters={
        "deepLinking": False,
        "operationsSorter": "alpha",
        "syntaxHighlight": True,
    },
    version="0.0.1",
)
