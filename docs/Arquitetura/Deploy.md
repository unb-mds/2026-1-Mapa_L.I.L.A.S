# Deploy e Nuvem (Vercel + Neon)

O projeto L.I.L.A.S. adota uma estratégia de implantação baseada em nuvem moderna utilizando soluções Serverless, garantindo alta disponibilidade, zero configuração de servidores tradicionais e escala automática conforme a demanda de acessos aos dados.

## Frontend e Backend: Vercel

Utilizamos a [Vercel](https://vercel.com/) como nossa principal plataforma de orquestração de deploy tanto para o ecossistema frontend quanto para a API backend.

* **Frontend (React + Vite):** A Vercel constrói os assets estáticos gerados pelo Vite e os distribui por sua Edge Network global (CDN). Isso garante que o dashboard e gráficos carreguem instantaneamente para usuários de qualquer lugar do Brasil.
* **Backend (FastAPI):** Tiramos proveito do ambiente Serverless Functions da Vercel. Embora o FastAPI seja um servidor web contínuo, a Vercel encapsula seus endpoints em funções que "acordam" e processam as requisições HTTP (como agregação de gráficos ou envio de PLs).
* **Integração Contínua Embutida:** Através da configuração do arquivo `vercel.json` e dos webhooks conectados ao repositório principal no GitHub, cada push ou merge na branch `main` dispara um novo ciclo de build, testando e publicando as atualizações no domínio de produção automaticamente.

## Banco de Dados: Neon (Serverless Postgres)

A persistência de dados brutos e os relacionamentos dos PLs são orquestrados através do [Neon](https://neon.tech/), um provedor de PostgreSQL nativo para a nuvem construído para rodar em modo serverless.

* **Separação de Armazenamento e Computação:** A arquitetura do Neon permite que o armazenamento dos milhares de PLs JSONB e a capacidade de processamento sejam geridos de modo independente. Se não há requisições, o banco entra em modo "scale-to-zero" (poupando custos).
* **Integração com Vercel:** A URI de conexão (`DATABASE_URL`) é fornecida via variáveis de ambiente para a Vercel, permitindo que as funções Serverless conectem-se de maneira veloz via pooling diretamente ao ambiente Neon.

Essa arquitetura descentralizada, combinada com os testes da Pipeline e o ambiente Docker local (para desenvolvimento e simulacões), criou um fluxo DevOps altamente robusto para o sistema.
