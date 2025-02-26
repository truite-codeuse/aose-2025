#!/bin/bash

# Prompt user for RAISON_API_KEY
echo "Enter your RAISON_API_KEY: "
read -s RAISON_API_KEY

# Create .env file in the current directory
echo "[INFO] Creating .env file..."
echo "RAISON_API_KEY = \"$RAISON_API_KEY\"" > .env

echo "[INFO] .env file created successfully."

echo "[INFO] Starting FastAPI application..."
curl -X POST 0.0.0.0:8002/match_for_scenario -H "Content-Type: application/json" \
    -d "{\"user_input\": \"I'm wondering if I should ban someone from my discord server\", \"get_max\": true}"