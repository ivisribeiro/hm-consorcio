FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte
COPY . .

# Cria diretório para arquivos estáticos
RUN mkdir -p /app/static/images

# Define variável de ambiente para porta
ENV PORT=8000

# Expõe a porta
EXPOSE $PORT

# Comando de produção
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
