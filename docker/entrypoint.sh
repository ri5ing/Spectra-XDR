#!/bin/bash
set -e

echo "========================================================"
echo " Starting SPECTRA-XDR Container Execution Environment  "
echo "========================================================"

echo "--> Waiting for PostgreSQL Database readiness..."
python -c "
import time, socket, urllib.parse, os
db_url = os.getenv('DATABASE_URL', '')
if db_url:
    try:
        url = urllib.parse.urlparse(db_url)
        host = url.hostname or 'postgres'
        port = url.port or 5432
        for _ in range(30):
            try:
                s = socket.create_connection((host, port), timeout=2)
                s.close()
                print(f'Database {host}:{port} is reachable.')
                break
            except Exception:
                time.sleep(1)
    except Exception as e:
        print(f'Database connection check failed: {e}')
" || true

echo "--> Applying Alembic Database Migrations..."
alembic upgrade head

# Background pull of Ollama LLM model if URL is configured
if [ -n "$OLLAMA_BASE_URL" ]; then
    (
        MODEL_NAME="${OLLAMA_MODEL:-llama3}"
        echo "--> Initiating background pull for Ollama model '${MODEL_NAME}' at ${OLLAMA_BASE_URL}..."
        for i in {1..30}; do
            if curl -s -f "${OLLAMA_BASE_URL}/api/tags" > /dev/null 2>&1; then
                echo "--> Ollama service detected. Downloading model '${MODEL_NAME}'..."
                curl -s -X POST "${OLLAMA_BASE_URL}/api/pull" -H "Content-Type: application/json" -d "{\"name\": \"${MODEL_NAME}\", \"stream\": false}" > /dev/null 2>&1 || true
                echo "--> Ollama model '${MODEL_NAME}' pull triggered."
                break
            fi
            sleep 2
        done
    ) &
fi

echo "--> Launching FastAPI Backend Server..."
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000

