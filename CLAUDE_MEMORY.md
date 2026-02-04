# HM Consórcio - CRM System - Memória do Projeto

> **NOTA**: Este arquivo é atualizado conforme o projeto evolui.
> Leia também: `CLAUDE.md` para instruções e melhores práticas.

---

## Visão Geral
Sistema CRM para gestão de consórcios da HM Capital. Backend em Python/FastAPI, Frontend em React/Vite com Ant Design.

## Estrutura do Projeto

```
hm-consorcio/
├── backend/                    # FastAPI + SQLAlchemy
│   ├── app/
│   │   ├── api/v1/endpoints/   # Endpoints da API
│   │   ├── models/             # Modelos SQLAlchemy
│   │   ├── schemas/            # Schemas Pydantic
│   │   ├── services/           # Serviços (PDF generators, etc)
│   │   └── core/               # Config, database, security
│   └── venv/                   # Virtual environment
│
└── frontend/                   # React + Vite + Ant Design
    └── src/
        ├── api/                # Chamadas à API
        ├── components/         # Componentes reutilizáveis
        ├── contexts/           # AuthContext
        └── pages/              # Páginas do sistema
```

## Módulos Implementados

### 1. Autenticação
- Login com JWT
- Proteção de rotas
- AuthContext

### 2. Clientes (`/clientes`)
- CRUD completo
- Formulário em accordion (Collapse) - todas seções abertas por padrão
- Seções: Dados Pessoais, Endereço, Documentos, Dados Profissionais, Dados Bancários, Cônjuge, Compromissos Financeiros, Preferências
- Arquivos:
  - `frontend/src/pages/Clientes/index.jsx` (listagem)
  - `frontend/src/pages/Clientes/ClienteForm.jsx` (formulário accordion)

### 3. Benefícios (`/beneficios`)
- CRUD completo
- Vinculado a Cliente, Tabela de Crédito, Administradora, Representante
- **Workflow de Status com Histórico**:
  - rascunho → simulacao → proposta → analise → aprovado → contrato_gerado → assinado → ativo → contemplado/cancelado
- Botões Avançar/Voltar status com registro de histórico
- Model `BeneficioHistorico` para rastrear transições
- Tipos de bem: imovel, carro, moto
- Arquivos:
  - `frontend/src/pages/Beneficios/index.jsx`
  - `frontend/src/pages/Beneficios/BeneficioForm.jsx`
  - `frontend/src/pages/Beneficios/BeneficioDetail.jsx`
  - `backend/app/models/beneficio_historico.py`

### 4. Cadastros Auxiliares
- **Usuários** (`/usuarios`) - CRUD com perfis
- **Unidades** (`/unidades`) - Filiais/unidades de venda
- **Empresas** (`/empresas`) - Empresas parceiras
- **Tabelas de Crédito** (`/tabelas-credito`) - Planos de consórcio com importação CSV
- **Administradoras** (`/administradoras`) - Administradoras de consórcio
- **Perfis** (`/perfis`) - Sistema de perfis e permissões customizáveis
- **Representantes** (`/representantes`) - Representantes de vendas
- **Consultores** (`/consultores`) - Consultores de consórcio

### 5. Relatórios (`/relatorios`)
- **Ficha de Atendimento**: PDF de 3 páginas
  - Capa profissional
  - Cadastro Pessoa Física
  - Proposta de Orçamento
  - Seleciona cliente → gera PDF

- **Contrato de Venda**: PDF de 10 páginas (modelo Capital Banq)
  - Página 1: Contrato Principal + Dados do Cliente
  - Página 2: Definições e Obrigações
  - Página 3: Obrigações e Condições
  - Página 4: Disposições Gerais
  - Página 5: Declarações e PEP
  - Página 6: Declaração de Ciência
  - Página 7: Termo de Consultoria (versão 1)
  - Página 8: Termo de Consultoria (versão 2)
  - Página 9: Questionário de Checagem
  - Página 10: Ciência da Análise Creditícia
  - Seleciona cliente → benefício → gera PDF

- **Termo de Adesão**: PDF de 3 páginas
  - Seleciona cliente → benefício → gera PDF

## Arquivos de Geração de PDF

### `backend/app/services/ficha_cliente_pdf.py`
- Classe `FichaClientePDFGenerator`
- Gera Ficha de Atendimento (3 páginas)
- Cor dourada (#C4A962) para headers
- Recebe: cliente, representante

### `backend/app/services/contrato_venda_pdf.py`
- Classe `ContratoVendaPDFGenerator`
- Gera Contrato de Venda (10 páginas)
- Cor teal/azul (#2E7D8A) para headers
- Recebe: cliente, beneficio, representante, empresa (opcional)

### `backend/app/services/termo_adesao_pdf_generator.py`
- Classe `TermoAdesaoPDFGenerator`
- Gera Termo de Adesão (3 páginas)
- Recebe: cliente, beneficio, usuario, empresa (opcional)

## Endpoints da API

### Relatórios
- `GET /api/v1/relatorios/ficha-atendimento/{cliente_id}/pdf` - Ficha de Atendimento (3 páginas)
- `GET /api/v1/relatorios/contrato/{beneficio_id}/pdf` - Contrato de Venda (10 páginas)
- `GET /api/v1/relatorios/termo-adesao/{beneficio_id}/pdf` - Termo de Adesão (3 páginas)
- `GET /api/v1/relatorios/cliente/{id}/pdf` - PDF antigo do cliente
- `GET /api/v1/relatorios/beneficio/{id}/pdf` - PDF do Benefício

### Benefícios
- `GET /api/v1/beneficios` - Lista benefícios
- `POST /api/v1/beneficios` - Cria benefício
- `GET /api/v1/beneficios/{id}` - Detalhes
- `PUT /api/v1/beneficios/{id}` - Atualiza
- `DELETE /api/v1/beneficios/{id}` - Remove
- `POST /api/v1/beneficios/{id}/avancar` - Avança status
- `POST /api/v1/beneficios/{id}/voltar` - Volta status
- `GET /api/v1/beneficios/{id}/historico` - Histórico de transições

### Perfis e Permissões
- `GET /api/v1/perfis` - Lista perfis
- `POST /api/v1/perfis` - Cria perfil
- `GET /api/v1/perfis/{id}` - Detalhes
- `PUT /api/v1/perfis/{id}` - Atualiza
- `DELETE /api/v1/perfis/{id}` - Remove

### Representantes
- `GET /api/v1/representantes` - Lista
- `POST /api/v1/representantes` - Cria
- `GET /api/v1/representantes/{id}` - Detalhes
- `PUT /api/v1/representantes/{id}` - Atualiza
- `DELETE /api/v1/representantes/{id}` - Remove

### Consultores
- `GET /api/v1/consultores` - Lista
- `POST /api/v1/consultores` - Cria
- `GET /api/v1/consultores/{id}` - Detalhes
- `PUT /api/v1/consultores/{id}` - Atualiza
- `DELETE /api/v1/consultores/{id}` - Remove

### Dashboard
- `GET /api/v1/dashboard/metricas` - Métricas gerais
- `GET /api/v1/dashboard/atividades-recentes` - Atividades recentes

### Outros
- `/api/v1/auth/login` - Login
- `/api/v1/clientes` - CRUD Clientes
- `/api/v1/usuarios` - CRUD Usuários
- `/api/v1/unidades` - CRUD Unidades
- `/api/v1/empresas` - CRUD Empresas
- `/api/v1/tabelas-credito` - CRUD Tabelas (com importação CSV)
- `/api/v1/administradoras` - CRUD Administradoras

## Como Rodar

### Backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd frontend
npm run dev
```

## Banco de Dados
- SQLite: `backend/app.db`
- Modelos em: `backend/app/models/`

## Cores do Sistema
- Azul principal (Ant Design): `#1890ff`
- Teal/Azul (Contrato de Venda): `#2E7D8A`
- Dourado (Ficha): `#C4A962`

## Arquivos de Logo
- `frontend/public/images/logo-white-bg.jpg` - Logo fundo branco (Login, PDFs)
- `frontend/public/images/logo-dark-bg.jpg` - Logo fundo escuro (Sidebar)
- `backend/app/static/images/logo-white-bg.jpg` - Logo para geração de PDFs

## Deploy (Render.com)

### URLs de Produção
- **Frontend**: https://frontend-production-f134.up.railway.app
- **Backend API**: https://hm-consorcio-api.onrender.com
- **GitHub**: https://github.com/ivisribeiro/hm-consorcio

### Credenciais de Acesso (Produção)
- **Email**: admin@crmconsorcio.com.br
- **Senha**: admin123

## Última Atualização
- Data: 2026-02-04
- Última tarefa: Migração do Contrato de Venda para WeasyPrint com layout moderno
- Status: Sistema em produção (v10)

### Correções do Deploy (2026-01-28)
1. **Tabela `perfis` vazia** - Inseridos perfis padrão via endpoint `/debug/fix-usuarios`
2. **Coluna `perfil_id` ausente em `usuarios`** - Adicionada coluna e FK
3. **Tabela `permissoes` vazia** - Populada via endpoint `/debug/seed-permissoes`
4. **Coluna `empresa_id` ausente em `unidades`** - Adicionada via endpoint `/debug/fix-unidades-table`

---

## Histórico de Alterações

| Data | Alteração |
|------|-----------|
| 2026-01-23 | Criação inicial do projeto |
| 2026-01-23 | Implementação de Clientes, Benefícios, Cadastros |
| 2026-01-23 | PDF Ficha de Atendimento, Contrato, Termo de Adesão |
| 2026-01-26 | Deploy no Render.com (Frontend + Backend + PostgreSQL) |
| 2026-01-27 | Sistema de Perfis e Permissões customizáveis |
| 2026-01-27 | CRUD de Representantes e Consultores |
| 2026-01-27 | Histórico de transições de status (BeneficioHistorico) |
| 2026-01-27 | Botões Avançar/Voltar status no BeneficioDetail |
| 2026-01-27 | Nova Ficha de Atendimento (3 páginas) com FichaClientePDFGenerator |
| 2026-01-27 | Novo Contrato de Venda (10 páginas) com ContratoVendaPDFGenerator |
| 2026-01-27 | Remoção do módulo Contratos antigo (substituído por PDF generator) |
| 2026-01-27 | Importação CSV para Tabelas de Crédito |
| 2026-01-28 | Correção de bugs do deploy (perfis, permissões, empresa_id) |
| 2026-02-04 | Migração do Contrato de Venda de ReportLab para WeasyPrint (HTML/CSS) |
| 2026-02-04 | Novo layout moderno: cards arredondados, pills, flex rows, footer absoluto |
| 2026-02-04 | Adicionadas dependências WeasyPrint no Dockerfile e requirements.txt |
| 2026-02-04 | Logo Capital Banq adicionada (backend/app/static/images/logo-capital-banq.png) |

---

## Próximas Tarefas Sugeridas

1. [x] Revisar PDFs de relatórios (ajustes visuais) - Contrato migrado para WeasyPrint
2. [ ] Implementar gráficos no Dashboard
3. [ ] Adicionar filtros avançados nas listagens
4. [ ] Implementar exportação de relatórios em Excel
5. [ ] Integração com assinatura digital
6. [ ] Notificações por email/WhatsApp
7. [ ] Relatórios de comissões

---

## Notas Importantes

1. Usar "HM CAPITAL" como nome da empresa nos PDFs
2. Formulário de Cliente usa Collapse (accordion), não Tabs
3. Todos os painéis do accordion abrem por padrão
4. Contrato de Venda usa WeasyPrint (HTML/CSS), cor teal (#178AA0), layout com cards arredondados
5. Módulo de Contratos foi removido - usar PDF generator diretamente
6. WeasyPrint requer dependências de sistema no Dockerfile (pango, cairo, gdk-pixbuf)
