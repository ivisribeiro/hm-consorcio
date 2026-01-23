# PROMPT PARA CLAUDE CODE - Sistema CRM de Consórcios

## Contexto do Projeto

Desenvolva um **Sistema CRM completo para gestão de consórcios** com cadastro de clientes, geração de benefícios, contratos e termos de adesão. O sistema deve seguir um fluxo específico de vendas desde o agendamento até a finalização com assinatura digital.

## Stack Tecnológica Obrigatória

**Backend:**
- Python 3.11+
- FastAPI (framework web)
- PostgreSQL (banco de dados)
- SQLAlchemy (ORM)
- Alembic (migrations)
- Pydantic (validação)
- JWT (autenticação)
- Redis (cache - opcional)

**Frontend:**
- React 18+
- Vite (build tool)
- Ant Design (UI framework)
- Axios (HTTP client)
- React Router v6
- React Hook Form ou Formik

## Fluxo de Negócio Completo

```
1. Consultor agenda com cliente
2. Representante atende e cadastra cliente completo
3. Representante gera um ou mais benefícios baseado em tabelas pré-definidas
4. Sistema gera RELATÓRIO EXPLICATIVO em PDF
5. Cliente analisa e decide aceitar ou rejeitar
6. Se aceitar: Sistema gera CONTRATO OFICIAL em PDF
7. Cliente assina o contrato (física ou digitalmente)
8. Representante cadastra na ADMINISTRADORA
9. Administradora retorna GRUPO e COTA
10. Sistema gera TERMO DE ADESÃO com grupo/cota
11. Cliente assina digitalmente o termo
12. ✅ Venda finalizada - Benefício ATIVO
```

## Modelo de Dados Completo

### CLIENTE (Cadastro Principal)

**Dados Básicos:**
- Natureza: Física ou Jurídica (radio)
- Unidade (dropdown - obrigatório)
- Empresa (dropdown - opcional)
- Nome (texto - obrigatório)
- CPF (máscara 999.999.999-99 + validação Receita Federal)
- Identidade, Órgão Expedidor, Data Expedição
- Sexo (dropdown: Feminino, Masculino, Outro)
- Data de Nascimento
- Nacionalidade, Naturalidade
- Nome da Mãe, Nome do Pai
- Estado Civil (dropdown)
- Cônjuge: Nome, Data Nascimento, CPF
- Telefone (obrigatório)
- Endereço
- Email

**Compromissos Financeiros** (cada um com Sim/Não + Prazo + Valor):
- Consórcio
- Empréstimos no Contracheque
- Empréstimos, Leasing, CDC, Crediário
- Financiamento Estudantil
- Financiamento Veicular
- Financiamento Habitacional
- Aluguel
- Outras Dívidas Não Declaradas
- Possui Restrição? (Sim/Não)
- Tentou Obter Crédito nos Últimos 12 Meses? (Sim/Não)

**Dados Profissionais:**
- Empresa
- Cargo
- Salário (R$)

**Preferências do Cliente:**
- Parcela Máxima
- Valor Carta
- Taxa Inicial

**Dados Bancários:**
- Banco
- Chave PIX
- Tipo Conta
- Agência
- Conta

**Observações:**
- Campo de texto livre

### BENEFÍCIO (Objeto principal do sistema)

**Relacionamentos:**
- Cliente
- Representante
- Consultor
- Empresa
- Unidade

**Dados do Benefício:**
- Prazo Grupo (vem da tabela)
- Valor do Crédito (vem da tabela)
- Parcela (vem da tabela)
- Índice Correção: INCC (fixo)
- Fundo de Reserva (vem da tabela)
- Seguro Prestamista: 0% (fixo)
- Taxa Adm Total: 26% (fixo)
- Valor Demais Parcelas
- Tipo Bem: Imóvel, Carro ou Moto
- Grupo (só após cadastro na administradora)
- Cota (só após cadastro na administradora)
- Qtd Participantes: 4076 (fixo)
- Tipo Plano: Normal (fixo)

**Status do Benefício:**
- Rascunho
- Proposto
- Aceito
- Rejeitado
- Contrato Gerado
- Contrato Assinado
- Aguardando Cadastro
- Cadastrado
- Termo Gerado
- Ativo
- Cancelado

### TABELA_CREDITO (Tabelas Pré-definidas)

Tabela com valores pré-calculados contendo:
- Prazo (meses)
- Valor do Crédito (R$)
- Parcela Mensal (R$)
- Fundo de Reserva (%)
- Taxa de Administração (%)
- Tipo de Bem (Imóvel/Carro/Moto)

**Exemplo de dados:**
```sql
prazo=120, valor_credito=50000, parcela=450, fundo_reserva=2.5%, tipo_bem='Imóvel'
prazo=120, valor_credito=100000, parcela=900, fundo_reserva=2.5%, tipo_bem='Imóvel'
prazo=80, valor_credito=30000, parcela=400, fundo_reserva=3.0%, tipo_bem='Carro'
prazo=60, valor_credito=15000, parcela=280, fundo_reserva=3.5%, tipo_bem='Moto'
```

### Outras Entidades

- **UNIDADES**: Cadastro de unidades/filiais
- **EMPRESAS**: Empresas parceiras
- **REPRESENTANTES**: Vendedores que atendem clientes
- **CONSULTORES**: Profissionais que agendam
- **ADMINISTRADORAS**: Empresas que gerenciam consórcios
- **CONTRATOS**: Contratos gerados para benefícios
- **TERMOS_ADESAO**: Termos finais com assinatura digital
- **ASSINATURAS**: Registro de assinaturas (física/digital)
- **DOCUMENTOS**: Arquivos anexados (RG, CPF, comprovantes)
- **USUARIOS**: Sistema de login e permissões

## Funcionalidades Obrigatórias

### 1. Sistema de Autenticação
- Login com email/senha
- JWT com access token e refresh token
- Níveis de permissão: Admin, Gerente, Representante, Consultor
- Recuperação de senha via email

### 2. CRUD Completo de Clientes
- Cadastro com TODAS as seções (dados básicos, compromissos, profissionais, bancários)
- Validação de CPF na Receita Federal (botão no formulário)
- Busca de CEP automática (integração ViaCEP)
- Listagem com filtros, ordenação e paginação
- Edição completa
- Visualização detalhada
- Soft delete (não deletar fisicamente)

### 3. Gestão de Benefícios
- Criar benefício baseado nas tabelas pré-definidas
- Simulador: usuário escolhe tipo de bem + valor desejado → sistema mostra opções de prazo/parcela
- Um cliente pode ter múltiplos benefícios
- Validar capacidade de pagamento (parcela não pode exceder 30% do salário)
- Workflow de status (Rascunho → Proposto → Aceito → etc.)

### 4. Geração de Documentos PDF

**Relatório Explicativo:**
- Gerado quando benefício é marcado como "Proposto"
- Apresenta: dados do cliente, benefício, simulações, condições
- Documento para o cliente analisar

**Contrato Oficial:**
- Gerado quando cliente aceita
- Contrato formal com todas as cláusulas
- Espaço para assinatura

**Termo de Adesão:**
- Gerado após cadastro na administradora
- Inclui Grupo e Cota
- Preparado para assinatura digital

### 5. Cadastro na Administradora
- Interface para enviar benefício para administradora
- Simular chamada de API (pode ser mock no primeiro momento)
- Receber e armazenar Grupo e Cota
- Atualizar status do benefício

### 6. Sistema de Assinaturas
- Registrar assinatura física de contrato
- Preparar para assinatura digital de termo (pode ser simulado)
- Armazenar hash do documento
- Registrar data, IP, localização

### 7. Dashboard e Relatórios
- Métricas principais (total clientes, benefícios ativos, pipeline)
- Gráfico de pipeline de vendas
- Filtros por período, representante, unidade

### 8. Cadastros Auxiliares
- CRUD de Unidades
- CRUD de Empresas
- CRUD de Representantes
- CRUD de Tabelas de Crédito
- CRUD de Administradoras

## Requisitos Técnicos Específicos

### Backend

**Estrutura de Pastas:**
```
backend/
├── app/
│   ├── api/v1/endpoints/     # Rotas da API
│   ├── models/               # Models SQLAlchemy
│   ├── schemas/              # Schemas Pydantic
│   ├── services/             # Lógica de negócio
│   ├── repositories/         # Acesso a dados
│   ├── core/                 # Config, segurança, DB
│   ├── utils/                # Validadores, helpers
│   └── templates/            # Templates HTML para PDF
├── alembic/                  # Migrations
├── tests/                    # Testes
├── .env.example
├── requirements.txt
├── docker-compose.yml
└── README.md
```

**Dependências Principais (requirements.txt):**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0
requests==2.31.0
weasyprint==60.1  # ou reportlab
jinja2==3.1.2
redis==5.0.1
slowapi==0.1.9
pytest==7.4.3
httpx==0.25.2
```

**Configurações (.env):**
```
DATABASE_URL=postgresql://crm_user:password@localhost:5432/crm_db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=email@example.com
SMTP_PASSWORD=senha

REDIS_URL=redis://localhost:6379
```

**Validações Críticas:**
- CPF único no sistema
- CPF válido (algoritmo + API Receita Federal opcional)
- Email válido
- Telefone formatado
- CEP válido
- Parcela não pode exceder 30% do salário
- Soma de compromissos não pode exceder 70% da renda

**Migrations (Alembic):**
- Criar estrutura completa do banco
- Popular tabelas iniciais (unidades, tabelas de crédito)
- Seed de usuário admin

### Frontend

**Estrutura de Pastas:**
```
frontend/
├── src/
│   ├── api/                  # Configuração Axios + endpoints
│   ├── components/
│   │   ├── common/           # Layout, Header, Sidebar
│   │   ├── forms/            # Formulários reutilizáveis
│   │   └── tables/           # Tabelas reutilizáveis
│   ├── pages/
│   │   ├── Login/
│   │   ├── Dashboard/
│   │   ├── Clientes/         # List, Create, Edit, View
│   │   ├── Beneficios/
│   │   ├── Contratos/
│   │   └── Configuracoes/
│   ├── hooks/                # Custom hooks
│   ├── contexts/             # Context API
│   ├── routes/               # Configuração rotas
│   ├── utils/                # Helpers, validators
│   └── styles/               # CSS global
├── .env.example
├── package.json
├── vite.config.js
└── README.md
```

**Dependências (package.json):**
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "antd": "^5.12.0",
    "axios": "^1.6.2",
    "react-hook-form": "^7.48.2",
    "dayjs": "^1.11.10",
    "@ant-design/icons": "^5.2.6",
    "react-input-mask": "^2.0.4"
  }
}
```

**Componentes Importantes:**

1. **ClienteForm**: Formulário com abas (Tabs) para cada seção
2. **CPFInput**: Input com máscara + botão validar
3. **CEPInput**: Input com busca automática de endereço
4. **PhoneInput**: Input com máscara de telefone
5. **MoneyInput**: Input formatado para moeda
6. **BeneficioSimulator**: Simulador de parcelas
7. **ClienteTable**: Tabela com filtros e paginação
8. **Dashboard**: Cards com métricas + gráficos

**Validações no Frontend:**
- Campos obrigatórios
- Formatos (CPF, email, telefone)
- Valores mínimos/máximos
- Datas válidas
- Máscaras de input

**Responsividade:**
- Mobile-first design
- Layout adaptável para tablet e desktop
- Ant Design Grid System

## Boas Práticas Obrigatórias

### Segurança
- ✅ Senhas hasheadas com bcrypt
- ✅ JWT com refresh token
- ✅ Validação de dados backend E frontend
- ✅ CORS configurado
- ✅ Rate limiting em endpoints críticos
- ✅ SQL Injection prevention (usando ORM)
- ✅ XSS prevention (sanitização)
- ✅ HTTPS em produção
- ✅ Logs de auditoria

### Performance
- ✅ Paginação em listagens
- ✅ Índices no banco de dados
- ✅ Lazy loading de componentes React
- ✅ Cache de consultas frequentes (Redis)
- ✅ Compression de respostas

### Código
- ✅ Código limpo e comentado
- ✅ Nomenclatura clara (português ou inglês consistente)
- ✅ Tratamento de erros centralizado
- ✅ Logs estruturados
- ✅ Testes unitários básicos
- ✅ Documentação (README completo)
- ✅ Type hints no Python
- ✅ PropTypes ou TypeScript no React

### DevOps
- ✅ Docker Compose para desenvolvimento
- ✅ Variáveis de ambiente (.env)
- ✅ Scripts de inicialização
- ✅ Migrations versionadas
- ✅ Seed data para testes

## Ordem de Implementação Sugerida

### Fase 1 - Fundação (1-2 dias)
1. Setup do projeto (backend + frontend)
2. Configuração do banco de dados
3. Sistema de autenticação (login/logout)
4. Layout base do frontend

### Fase 2 - Cliente (2-3 dias)
5. Models e migrations de Cliente
6. API de clientes (CRUD completo)
7. Formulário de cadastro de cliente (todas as seções)
8. Listagem e visualização de clientes
9. Validação de CPF
10. Busca de CEP

### Fase 3 - Benefícios (2-3 dias)
11. Models de Benefício e Tabela de Crédito
12. Seed das tabelas de crédito
13. API de benefícios
14. Simulador de benefícios
15. Formulário de criação de benefício
16. Listagem de benefícios

### Fase 4 - Documentos (2-3 dias)
17. Service de geração de PDF
18. Templates HTML dos documentos
19. Endpoint de relatório explicativo
20. Endpoint de contrato oficial
21. Endpoint de termo de adesão
22. Preview e download de PDFs

### Fase 5 - Workflow (1-2 dias)
23. Implementar transições de status
24. Cadastro na administradora (mock)
25. Sistema de assinaturas
26. Notificações por email

### Fase 6 - Cadastros Auxiliares (1 dia)
27. CRUD de Unidades
28. CRUD de Empresas
29. CRUD de Representantes
30. CRUD de Tabelas de Crédito

### Fase 7 - Dashboard e Finalização (1 dia)
31. Dashboard com métricas
32. Relatórios gerenciais
33. Testes
34. Documentação final
35. Docker compose

## Entregáveis Finais

1. ✅ Código completo backend (Python/FastAPI)
2. ✅ Código completo frontend (React/Ant Design)
3. ✅ Banco de dados estruturado (PostgreSQL)
4. ✅ Migrations (Alembic)
5. ✅ Docker Compose configurado
6. ✅ README detalhado com:
   - Instruções de instalação
   - Como rodar o projeto
   - Estrutura de pastas
   - Variáveis de ambiente
   - Endpoints da API
7. ✅ .env.example
8. ✅ Seed data (usuário admin + dados de teste)
9. ✅ Testes básicos

## Comandos de Inicialização

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
python scripts/seed_data.py
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Docker (tudo junto):**
```bash
docker-compose up -d
```

## Observações Importantes

1. **Foco no Fluxo**: O sistema deve seguir exatamente o fluxo de negócio descrito
2. **Validações**: Implementar validações rigorosas tanto no backend quanto frontend
3. **UX/UI**: Interface intuitiva e profissional usando Ant Design
4. **Documentos PDF**: Devem ser profissionais e prontos para uso real
5. **Segurança**: Não comprometer em aspectos de segurança
6. **Escalabilidade**: Código preparado para crescer
7. **Manutenibilidade**: Código limpo e bem estruturado

## Dúvidas ou Ajustes?

- Se algo não estiver claro, pergunte antes de implementar
- Siga as boas práticas de cada tecnologia
- Priorize código funcional e testável
- Documente decisões importantes

---

**COMECE PELA FASE 1 E AVANCE PROGRESSIVAMENTE. BOA SORTE! 🚀**
