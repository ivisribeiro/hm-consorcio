# CRM Consórcios

Sistema CRM completo para gestão de consórcios com cadastro de clientes, geração de benefícios, contratos e termos de adesão.

## Stack Tecnológica

### Backend
- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy + Alembic
- JWT para autenticação
- Redis (cache)

### Frontend
- React 18+
- Vite
- Ant Design
- Axios
- React Router v6

## Estrutura do Projeto

```
hm-consorcio/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/    # Rotas da API
│   │   ├── models/              # Models SQLAlchemy
│   │   ├── schemas/             # Schemas Pydantic
│   │   ├── services/            # Lógica de negócio
│   │   ├── repositories/        # Acesso a dados
│   │   ├── core/                # Config, segurança, DB
│   │   ├── utils/               # Validadores, helpers
│   │   └── templates/           # Templates HTML para PDF
│   ├── alembic/                 # Migrations
│   ├── tests/                   # Testes
│   ├── scripts/                 # Scripts utilitários
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/                 # Configuração Axios
│   │   ├── components/          # Componentes React
│   │   ├── pages/               # Páginas da aplicação
│   │   ├── contexts/            # Context API
│   │   ├── hooks/               # Custom hooks
│   │   └── styles/              # CSS
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Configuração do Ambiente

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis (opcional)

### Variáveis de Ambiente

Copie os arquivos de exemplo:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### Backend

```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Criar banco de dados (PostgreSQL deve estar rodando)
# createdb crm_db

# Executar migrations
alembic upgrade head

# Executar seed de dados iniciais
python scripts/seed_data.py

# Iniciar servidor
uvicorn app.main:app --reload
```

O backend estará disponível em: http://localhost:8000
- Documentação Swagger: http://localhost:8000/docs
- Documentação ReDoc: http://localhost:8000/redoc

### Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm run dev
```

O frontend estará disponível em: http://localhost:5173

### Docker (tudo junto)

```bash
docker-compose up -d
```

## Usuários de Teste

Após executar o seed, os seguintes usuários estarão disponíveis:

| Perfil | Email | Senha |
|--------|-------|-------|
| Admin | admin@crmconsorcio.com.br | admin123 |
| Gerente | gerente@crmconsorcio.com.br | gerente123 |
| Representante | representante@crmconsorcio.com.br | repr123 |
| Consultor | consultor@crmconsorcio.com.br | cons123 |

## Endpoints da API

### Autenticação
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Dados do usuário atual
- `POST /api/v1/auth/logout` - Logout

### Usuários
- `GET /api/v1/usuarios` - Listar usuários
- `POST /api/v1/usuarios` - Criar usuário
- `GET /api/v1/usuarios/{id}` - Obter usuário
- `PUT /api/v1/usuarios/{id}` - Atualizar usuário
- `DELETE /api/v1/usuarios/{id}` - Desativar usuário

## Fluxo de Negócio

```
1. Consultor agenda com cliente
2. Representante atende e cadastra cliente completo
3. Representante gera benefícios baseado em tabelas pré-definidas
4. Sistema gera RELATÓRIO EXPLICATIVO em PDF
5. Cliente analisa e decide aceitar ou rejeitar
6. Se aceitar: Sistema gera CONTRATO OFICIAL em PDF
7. Cliente assina o contrato
8. Representante cadastra na ADMINISTRADORA
9. Administradora retorna GRUPO e COTA
10. Sistema gera TERMO DE ADESÃO
11. Cliente assina digitalmente o termo
12. Venda finalizada - Benefício ATIVO
```

## Deploy no Render (Gratuito)

### Pré-requisitos
1. Conta no [Render](https://render.com) (gratuita)
2. Repositório no GitHub

### Deploy Automático (Blueprint)

1. **Suba o código para o GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/SEU_USUARIO/hm-consorcio.git
   git push -u origin main
   ```

2. **Deploy no Render**
   - Acesse: https://dashboard.render.com/blueprints
   - Clique em "New Blueprint Instance"
   - Conecte seu repositório GitHub
   - O Render vai detectar automaticamente o arquivo `render.yaml`
   - Clique em "Apply" e aguarde o deploy

3. **Após o deploy**
   - Backend: https://hm-consorcio-api.onrender.com
   - Frontend: https://hm-consorcio-web.onrender.com
   - Banco de dados PostgreSQL criado automaticamente

### Deploy Manual

Se preferir deploy manual:

1. **Banco de Dados (PostgreSQL)**
   - Dashboard > New > PostgreSQL
   - Name: `hm-consorcio-db`
   - Plan: Free

2. **Backend (Web Service)**
   - Dashboard > New > Web Service
   - Connect repository
   - Name: `hm-consorcio-api`
   - Runtime: Docker
   - Plan: Free
   - Environment Variables:
     - `DATABASE_URL`: (Internal Database URL do PostgreSQL)
     - `SECRET_KEY`: (gere uma chave aleatória)
     - `DEBUG`: false
     - `CORS_ORIGINS`: https://hm-consorcio-web.onrender.com

3. **Frontend (Static Site)**
   - Dashboard > New > Static Site
   - Connect repository
   - Name: `hm-consorcio-web`
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/dist`
   - Environment Variables:
     - `VITE_API_URL`: https://hm-consorcio-api.onrender.com/api/v1

### Limitações do Plano Gratuito

- Backend "hiberna" após 15min sem uso (demora ~30s para acordar)
- Banco de dados: 256MB de armazenamento
- Logs: 24 horas de retenção

## Licença

Propriedade privada - Todos os direitos reservados.
