#!/bin/bash
set -e

echo "=== Executando migrations ==="
alembic upgrade head || echo "Migrations falharam ou já estão atualizadas"

echo "=== Iniciando servidor ==="
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
