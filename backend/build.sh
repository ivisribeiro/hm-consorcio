#!/bin/bash
# Script de build para Render

echo "=== Instalando dependências ==="
pip install --no-cache-dir -r requirements.txt

echo "=== Executando seed do banco de dados ==="
python scripts/seed_data.py || echo "Seed já executado ou falhou (ignorando)"

echo "=== Build concluído ==="
