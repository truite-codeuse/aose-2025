#!/bin/bash

echo "[INFO] Starting FastAPI application..."
uvicorn role6_service:app --host 0.0.0.0 --port 8006 --reload