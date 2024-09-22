#!/bin/bash

CODE_DIR="$(dirname $0)/.."
uvicorn src.src:app \
    --reload \
    --reload-delay 1 \
    --reload-dir $CODE_DIR \
    --reload-dir . \
    --reload-exclude '.venv/*' \
    --reload-exclude 'venv/*' \
    --reload-exclude 'data/*' \
    --reload-exclude 'db/*' \
    --reload-exclude 'logging.yaml' \
    --reload-include '*.py' \
    --ssl-keyfile=$CODE_DIR/deploy/ssl/privkey.pem \
    --ssl-certfile=$CODE_DIR/deploy/ssl/fullchain.pem \
    # --reload-include '*.yaml' \
    --port 14080 \
    --loop uvloop

