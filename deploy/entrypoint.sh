#!/bin/bash
set -e

# root needs this line to find 'aiml' script
PYTHONPATH="$PYTHONPATH:/app"

exec "$@"



