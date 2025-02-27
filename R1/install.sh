#!/bin/bash

echo "Setting up environment variables..."
cat > .env <<EOL
DATABASE_URL=postgresql://user:password@localhost:5432/db_name
EOL

echo "[INFO] .env file created. Adjust values as necessary."