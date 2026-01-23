FROM node:20-alpine

WORKDIR /app

# Copia arquivos de dependências
COPY package*.json ./

# Instala dependências
RUN npm install

# Copia o código fonte
COPY . .

# Expõe a porta
EXPOSE 5173

# Comando padrão
CMD ["npm", "run", "dev", "--", "--host"]
