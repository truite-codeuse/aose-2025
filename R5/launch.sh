#!/bin/bash

echo "[INFO] Starting FastAPI application..."
uvicorn role5_service:app --host 0.0.0.0 --port 8005