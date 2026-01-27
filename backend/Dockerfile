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

# Torna o script de startup executável
RUN chmod +x /app/start.sh

# Define variável de ambiente para porta
ENV PORT=8000

# Expõe a porta
EXPOSE $PORT

# Comando de produção (executa migrations e inicia servidor)
CMD ["/app/start.sh"]
