#!/bin/bash

# Step 4: Configure Environment Variables
echo "Setting up environment variables..."
cat > .env <<EOL
DATABASE_URL=postgresql://user:password@localhost:5432/db_name
EOL

echo "[INFO] .env file created. Adjust values as necessary."

# Step 5: Start the PostgreSQL Database with Docker Compose
echo "[INFO] Starting PostgreSQL with Docker Compose..."
docker-compose up -d

echo "[INFO] PostgreSQL is now running."

# Step 6: Run the FastAPI Application
echo "[INFO] Starting FastAPI application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000