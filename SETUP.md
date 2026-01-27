# Setup - AI Web Scraper Showcase

Guia completo para executar a aplicacao localmente e fazer deploy na Railway.

---

## Sumario

1. [Pre-requisitos](#pre-requisitos)
2. [Variaveis de Ambiente](#variaveis-de-ambiente)
3. [Executar Localmente](#executar-localmente)
4. [Deploy na Railway](#deploy-na-railway)
5. [Troubleshooting](#troubleshooting)

---

## Pre-requisitos

### Software Necessario

| Software | Versao Minima | Download |
|----------|---------------|----------|
| Python | 3.10+ | https://python.org/downloads |
| Node.js | 18+ | https://nodejs.org |
| Git | 2.0+ | https://git-scm.com |

### Verificar Instalacao

```bash
python --version   # Python 3.10+
node --version     # v18+
npm --version      # 9+
git --version      # 2+
```

---

## Variaveis de Ambiente

### OpenAI API Key

A aplicacao usa a API da OpenAI para o scraping inteligente. Cada usuario pode fornecer sua propria key, mas voce pode configurar uma key padrao para demos.

**Como obter:**

1. Acesse https://platform.openai.com
2. Faca login ou crie uma conta
3. Va em **API Keys** no menu lateral
4. Clique em **Create new secret key**
5. Copie a key (comeca com `sk-`)

> **Importante:** A key so e exibida uma vez. Guarde-a em local seguro.

### Tabela de Variaveis

#### Backend (.env)

| Variavel | Obrigatorio | Descricao | Exemplo |
|----------|-------------|-----------|---------|
| `DEBUG` | Nao | Modo debug | `false` |
| `MAX_CONCURRENT_SESSIONS` | Nao | Limite de usuarios simultaneos | `35` |
| `MAX_REQUESTS_PER_MINUTE` | Nao | Rate limit por sessao | `10` |
| `SESSION_TIMEOUT_MINUTES` | Nao | Tempo de expiracao da sessao | `30` |
| `CORS_ORIGINS` | Sim (prod) | URLs permitidas para CORS | `["https://seusite.com"]` |
| `DEFAULT_OPENAI_API_KEY` | Nao | API key padrao para demo | `sk-...` |

#### Frontend (.env.local)

| Variavel | Obrigatorio | Descricao | Exemplo |
|----------|-------------|-----------|---------|
| `NEXT_PUBLIC_API_URL` | Sim | URL do backend | `http://localhost:8000` |

---

## Executar Localmente

### Passo 1: Clonar o Repositorio

```bash
git clone <seu-repositorio>
cd showcase
```

### Passo 2: Configurar o Backend

```bash
# Entrar no diretorio do backend
cd backend

# Criar ambiente virtual Python
python -m venv venv

# Ativar ambiente virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar navegador para o Playwright
playwright install chromium
```

### Passo 3: Configurar Variaveis do Backend

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar o arquivo .env (opcional)
# nano .env  ou  code .env
```

Conteudo do `.env`:
```env
DEBUG=false
MAX_CONCURRENT_SESSIONS=35
MAX_REQUESTS_PER_MINUTE=10
SESSION_TIMEOUT_MINUTES=30
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]

# Opcional: sua API key padrao
# DEFAULT_OPENAI_API_KEY=sk-...
```

### Passo 4: Iniciar o Backend

```bash
# Ainda no diretorio backend/ com venv ativado
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Voce deve ver:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Started reloader process
```

**Testar:** Acesse http://localhost:8000/docs para ver a documentacao da API.

### Passo 5: Configurar o Frontend (novo terminal)

```bash
# Voltar para a raiz e entrar no frontend
cd frontend

# Instalar dependencias
npm install

# Copiar arquivo de ambiente
cp .env.local.example .env.local
```

Conteudo do `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Passo 6: Iniciar o Frontend

```bash
npm run dev
```

Voce deve ver:
```
▲ Next.js 16.x.x
- Local:        http://localhost:3000
```

### Passo 7: Testar a Aplicacao

1. Acesse http://localhost:3000
2. Insira sua OpenAI API Key
3. Selecione um modelo (GPT-4o Mini e mais economico)
4. Insira uma URL (ex: `https://news.ycombinator.com`)
5. Descreva o que extrair (ex: "Extraia os titulos das 10 primeiras noticias")
6. Clique em "Iniciar Scraping"

---

## Deploy na Railway

### Passo 1: Criar Conta na Railway

1. Acesse https://railway.app
2. Clique em **Login** ou **Start a New Project**
3. Faca login com GitHub (recomendado)

### Passo 2: Preparar Arquivos de Deploy

#### Backend - Criar Dockerfile

Crie o arquivo `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias do sistema para Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Playwright e navegador
RUN playwright install chromium --with-deps

# Copiar codigo da aplicacao
COPY . .

# Expor porta
EXPOSE 8000

# Comando para iniciar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend - Verificar next.config.ts

O Next.js ja esta configurado para build estatico. Nenhuma alteracao necessaria.

### Passo 3: Deploy do Backend na Railway

1. No dashboard da Railway, clique em **New Project**
2. Selecione **Deploy from GitHub repo**
3. Autorize o acesso ao seu repositorio
4. Selecione o repositorio
5. Railway detecta automaticamente o projeto

**Configurar o servico Backend:**

1. Clique no servico criado
2. Va em **Settings**
3. Em **Root Directory**, coloque: `showcase/backend`
4. Em **Build Command**, deixe vazio (usa Dockerfile)
5. Va em **Variables** e adicione:

| Variavel | Valor |
|----------|-------|
| `DEBUG` | `false` |
| `MAX_CONCURRENT_SESSIONS` | `35` |
| `MAX_REQUESTS_PER_MINUTE` | `10` |
| `SESSION_TIMEOUT_MINUTES` | `30` |
| `CORS_ORIGINS` | `["https://SEU-FRONTEND.up.railway.app"]` |

6. Va em **Settings** > **Networking** > **Generate Domain**
7. Anote a URL gerada (ex: `https://seu-backend.up.railway.app`)

### Passo 4: Deploy do Frontend na Railway

1. No mesmo projeto, clique em **New** > **GitHub Repo**
2. Selecione o mesmo repositorio
3. Isso cria um segundo servico

**Configurar o servico Frontend:**

1. Clique no novo servico
2. Va em **Settings**
3. Em **Root Directory**, coloque: `showcase/frontend`
4. Em **Build Command**, coloque: `npm run build`
5. Em **Start Command**, coloque: `npm start`
6. Va em **Variables** e adicione:

| Variavel | Valor |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | `https://seu-backend.up.railway.app` |

7. Va em **Settings** > **Networking** > **Generate Domain**

### Passo 5: Atualizar CORS do Backend

Apos ter a URL do frontend:

1. Volte ao servico do Backend
2. Va em **Variables**
3. Atualize `CORS_ORIGINS`:

```
["https://seu-frontend.up.railway.app"]
```

4. O servico reinicia automaticamente

### Passo 6: Verificar Deploy

1. Acesse a URL do frontend
2. Teste o scraping com sua API key
3. Verifique os logs em cada servico se houver erros

---

## Deploy Alternativo: Vercel (Frontend) + Railway (Backend)

Se preferir usar Vercel para o frontend (gratuito e otimizado para Next.js):

### Frontend na Vercel

1. Acesse https://vercel.com
2. Importe o repositorio do GitHub
3. Configure:
   - **Root Directory**: `showcase/frontend`
   - **Framework Preset**: Next.js (auto-detectado)
4. Adicione variavel de ambiente:
   - `NEXT_PUBLIC_API_URL`: URL do backend na Railway

### Atualizar CORS no Backend

Atualize a variavel `CORS_ORIGINS` no Railway para incluir a URL da Vercel:

```
["https://seu-projeto.vercel.app"]
```

---

## Estrutura de Custos

### Railway

| Plano | Limite | Custo |
|-------|--------|-------|
| Hobby | $5/mes de creditos | Gratuito |
| Pro | $20/mes + uso | Pago |

O plano Hobby e suficiente para showcase/portfolio.

### OpenAI API

| Modelo | Input | Output |
|--------|-------|--------|
| GPT-4o Mini | $0.15/1M tokens | $0.60/1M tokens |
| GPT-4o | $2.50/1M tokens | $10/1M tokens |
| GPT-4 Turbo | $10/1M tokens | $30/1M tokens |

**Estimativa:** Uma requisicao de scraping usa ~500-2000 tokens.
Com GPT-4o Mini, 1000 requisicoes custam aproximadamente $0.50.

---

## Troubleshooting

### Erro: "Playwright browsers not installed"

```bash
playwright install chromium --with-deps
```

### Erro: "CORS blocked"

Verifique se a URL do frontend esta na variavel `CORS_ORIGINS` do backend.

### Erro: "Connection refused" no frontend

1. Verifique se o backend esta rodando
2. Verifique a URL em `NEXT_PUBLIC_API_URL`
3. Teste acessando `http://localhost:8000/docs`

### Erro: "Rate limit exceeded"

Aguarde 1 minuto. O limite e de 10 requisicoes por minuto por sessao.

### Erro: "Invalid API key"

1. Verifique se a key comeca com `sk-`
2. Verifique se a key nao expirou
3. Verifique seu saldo na OpenAI

### Deploy falha na Railway

1. Verifique os logs em **Deployments**
2. Certifique-se que o `Root Directory` esta correto
3. Verifique se o Dockerfile esta no diretorio correto

---

## Comandos Uteis

### Desenvolvimento Local

```bash
# Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Frontend
cd frontend && npm run dev
```

### Build de Producao

```bash
# Backend (teste local)
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend && npm run build && npm start
```

### Verificar Saude da API

```bash
curl http://localhost:8000/api/v1/health
```

---

## Proximos Passos

1. Personalize o frontend com sua marca/cores
2. Adicione sua foto e links para redes sociais
3. Configure um dominio personalizado
4. Adicione Google Analytics para monitorar acessos
