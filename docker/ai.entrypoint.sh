#!/bin/bash
set -e

# Start server with Uvicorn - use port 5001
echo "Starting Adverse Media Screening AI server with Uvicorn..."

python -m uvicorn app.factory:create_app --factory --host 0.0.0.0 --port 5001 --reload