#!/bin/bash

echo ""
source .venv/bin/activate
export PYTHONPATH=./
uvicorn src.server:app --host 0.0.0.0 --port 8001