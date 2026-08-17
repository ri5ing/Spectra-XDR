#!/bin/bash
set -e

echo "========================================================"
echo " Starting SPECTRA-XDR Container Execution Environment  "
echo "========================================================"

echo "--> Applying Alembic Database Migrations..."
alembic upgrade head

echo "--> Launching FastAPI Backend Server..."
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000
