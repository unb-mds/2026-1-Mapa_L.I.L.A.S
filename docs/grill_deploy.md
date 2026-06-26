# Deploy L.I.L.A.S. Backend na Vercel

Configurar e publicar o backend FastAPI na Vercel via GitHub Actions (CI/CD automático),
com as correções necessárias no `vercel.json` e `database.py` para funcionar em ambiente serverless.

## Decisões Tomadas no Grill

| Tema | Decisão |
|------|---------|
| Root Directory | `backend/` no projeto Vercel |
| Variáveis de ambiente | `DATABASE_URL`, `GEMINI_API_KEY`, `USE_MOCK_IA=False` |
| CORS | `allow_origins=["*"]` por ora, restringir depois do deploy do frontend |
| `maxDuration` | 60s (máximo Hobby) |
| Python | `python-3.11` (alinhado com Dockerfile) |
| Connection pool | `NullPool` (correto para serverless) |
| Migrações | Não rodar — Neon já está populado |
| Deploy | GitHub Actions (CD automático a cada push na `main`) |
| Escopo CI/CD | Apenas backend por enquanto |
| Verificação | `GET /` + `GET /api/projetos-de-lei?per_page=5` |

---

## Proposed Changes

### 1. `backend/vercel.json` — Adicionar runtime Python + maxDuration

#### [MODIFY] [vercel.json](file:///c:/Users/willi/OneDrive/Documentos/Documentos/RENAN_DOCS/2026.1/MDS/Repo/2026-1-Squad2/backend/vercel.json)

```diff
 {
+    "version": 2,
     "builds": [
         {
             "src": "app/main.py",
-            "use": "@vercel/python"
+            "use": "@vercel/python",
+            "config": { "maxLambdaSize": "50mb" }
         }
     ],
     "routes": [
         {
             "src": "/(.*)",
             "dest": "app/main.py"
         }
     ],
+    "functions": {
+        "app/main.py": {
+            "maxDuration": 60,
+            "runtime": "python3.11"
+        }
+    }
 }
```

---

### 2. `backend/app/database.py` — Trocar para NullPool

#### [MODIFY] [database.py](file:///c:/Users/willi/OneDrive/Documentos/Documentos/RENAN_DOCS/2026.1/MDS/Repo/2026-1-Squad2/backend/app/database.py)

```diff
-from sqlalchemy import create_engine, text
+from sqlalchemy import create_engine, text
+from sqlalchemy.pool import NullPool

-engine = create_engine(DATABASE_URL, echo=False)
+engine = create_engine(DATABASE_URL, echo=False, poolclass=NullPool)
```

---

### 3. `.github/workflows/deploy-backend.yml` — Workflow de CD

#### [NEW] [deploy-backend.yml](file:///c:/Users/willi/OneDrive/Documentos/Documentos/RENAN_DOCS/2026.1/MDS/Repo/2026-1-Squad2/.github/workflows/deploy-backend.yml)

```yaml
name: Deploy Backend → Vercel

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Vercel CLI
        run: npm install -g vercel@latest

      - name: Deploy to Vercel
        run: vercel --cwd backend --prod --yes --token=${{ secrets.VERCEL_TOKEN }}
        env:
          VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
          VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}
```

---

## Secrets necessários no GitHub

Antes do primeiro push, configurar em **Settings → Secrets and variables → Actions**:

| Secret | Como obter |
|--------|-----------|
| `VERCEL_TOKEN` | [vercel.com/account/tokens](https://vercel.com/account/tokens) → "Create Token" |
| `VERCEL_ORG_ID` | Executar `vercel --cwd backend` localmente pela primeira vez → copiado do `.vercel/project.json` |
| `VERCEL_PROJECT_ID` | Idem acima |

---

## Variáveis de Ambiente na Vercel

Configurar no painel: **Vercel → projeto backend → Settings → Environment Variables**

| Variável | Valor | Environments |
|---------|-------|-------------|
| `DATABASE_URL` | `postgresql://neondb_owner:...@ep-...-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require` | Production, Preview |
| `GEMINI_API_KEY` | `AQ.Ab8...` | Production, Preview |
| `USE_MOCK_IA` | `False` | Production |
| `USE_MOCK_IA` | `True` | Preview (opcional, para testar sem gastar cota Gemini) |

> [!CAUTION]
> As chaves atuais no `.env` são **credenciais reais de produção**. Nunca commitá-las. Verificar que `backend/.env` está no `.gitignore`.

---

## Passo a Passo de Execução

### Etapa 0 — Pré-condição: Criar projeto na Vercel

1. Acessar [vercel.com/new](https://vercel.com/new)
2. Importar o repositório `2026-1-Squad2`
3. **Root Directory:** `backend`
4. **Framework Preset:** Other
5. **Build Command:** deixar vazio
6. **Output Directory:** deixar vazio
7. Adicionar as 3 variáveis de ambiente (tabela acima)
8. Clicar em **Deploy** (primeiro deploy manual para gerar o `.vercel/project.json`)
9. Anotar `VERCEL_ORG_ID` e `VERCEL_PROJECT_ID` do `.vercel/project.json` gerado

### Etapa 1 — Modificar `vercel.json`

Atualizar `backend/vercel.json` conforme diff acima (adicionar `functions`, `maxDuration: 60`, `runtime: python3.11`).

### Etapa 2 — Modificar `database.py`

Trocar `create_engine(DATABASE_URL, echo=False)` por `create_engine(DATABASE_URL, echo=False, poolclass=NullPool)`.

### Etapa 3 — Criar GitHub Actions workflow

Criar `.github/workflows/deploy-backend.yml` conforme template acima.

### Etapa 4 — Configurar secrets no GitHub

Adicionar `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` em **Settings → Secrets**.

### Etapa 5 — Push e verificar

```bash
git add backend/vercel.json backend/app/database.py .github/workflows/deploy-backend.yml
git commit -m "feat: configure backend deploy on Vercel"
git push origin main
```

Acompanhar o workflow em **Actions → Deploy Backend → Vercel**.

### Etapa 6 — Validação

```bash
# Substituir pela URL gerada pela Vercel
curl https://seu-backend.vercel.app/
# Esperado: {"status": "API L.I.L.A.S. Online"}

curl "https://seu-backend.vercel.app/api/projetos-de-lei?per_page=5"
# Esperado: {"projetos": [...], "total": N, ...}
```

---

## Verification Plan

### Automated (GitHub Actions)
- O workflow deve completar sem erro (status `✅`)
- Vercel mostra deployment status `Ready`

### Manual
- `GET /` → `{"status": "API L.I.L.A.S. Online"}`
- `GET /api/projetos-de-lei?per_page=5` → lista projetos do Neon
- `GET /api/projetos-de-lei/filtros` → retorna partidos, UFs, anos
- Checar logs na Vercel (Functions → Logs) para confirmar sem erros de conexão DB

> [!NOTE]
> O `popular_banco.py` (ingestão de dados) **não deve** e **não pode** rodar na Vercel — é um script de longa duração. Rodar localmente ou via GitHub Action separada com runner `ubuntu-latest` e timeout maior.
