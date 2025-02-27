#!/bin/bash

echo "[INFO] Starting PostgreSQL with Docker Compose..."
docker-compose up -d

echo "[INFO] PostgreSQL is now running."

echo "[INFO] Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000