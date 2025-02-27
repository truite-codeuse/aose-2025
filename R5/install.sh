#!/bin/bash

echo "Enter your RAISON_API_KEY: "
read -s RAISON_API_KEY

echo "[INFO] Creating config.py file..."
echo "api_key = \"$RAISON_API_KEY\"" > config.py

echo "[INFO] config.py file created successfully."