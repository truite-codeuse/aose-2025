#!/bin/bash

# Prompt user for RAISON_API_KEY
echo "Enter your RAISON_API_KEY: "
read -s RAISON_API_KEY

# Create config.py file with the API key
echo "[INFO] Creating config.py file..."
echo "api_key = \"$RAISON_API_KEY\"" > config.py

echo "[INFO] config.py file created successfully."