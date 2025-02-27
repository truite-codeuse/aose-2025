#!/bin/bash

echo "Enter your RAISON_API_KEY: "
read -s RAISON_API_KEY

echo "[INFO] Creating .env file..."
echo "RAISON_API_KEY = \"$RAISON_API_KEY\"" > .env

echo "[INFO] .env file created successfully."
