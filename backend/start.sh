#!/bin/bash

echo "======================================="
echo "=== HM Consorcio Backend Starting ==="
echo "======================================="
echo "PORT: ${PORT:-8000}"
echo "DATABASE_URL set: $(if [ -n "$DATABASE_URL" ]; then echo 'YES'; else echo 'NO'; fi)"
echo "======================================="

# Run migrations (they will skip if already applied)
echo "=== Running alembic migrations ==="
alembic upgrade head 2>&1 || {
    echo "=== Alembic failed, but continuing anyway ==="
}

echo "=== Starting uvicorn server ==="
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
