# Mapa L.I.L.A.S - Mapa Legislativo Informativo de Leis de Acompanhamento Social
---
Buscador de projetos de lei sobre: feminicídio, violência doméstica e direitos da mulher.
Plataforma para busca e acompanhamento de projetos de lei sobre feminicídio e visualização de gráficos sobre o assunto.
 
---
 
## Objetivo e Propósito

O **Mapa L.I.L.A.S.** democratiza o acesso à informação legislativa sobre o combate ao feminicídio e a proteção dos direitos da mulher no Brasil. O projeto atua como uma ponte entre o jargão jurídico/político e a sociedade, transformando os dados densos e fragmentados da Câmara dos Deputados e do Senado Federal em informações consolidadas e acessíveis. Dessa forma, cidadãos, jornalistas, pesquisadores e organizações civis podem monitorar o avanço (ou o bloqueio) de políticas públicas de forma centralizada.

## Inteligência Artificial e NLP

Como as APIs governamentais originais não possuem filtros exatos ou confiáveis por tema (apenas texto livre), a plataforma utiliza técnicas de **Inteligência Artificial focadas em Processamento de Linguagem Natural (NLP)** e algoritmos de extração (Regex) nativos em seu backend. O módulo classificador de IA é responsável por analisar semanticamente as ementas e os textos brutos de milhares de proposições legislativas, conseguindo identificar, classificar e categorizar de forma autônoma quais Projetos de Lei e PECs são pertinentes à temática de violência contra a mulher.

## Escopo
 
**O que a plataforma faz:**
- Busca e listagem de Projetos de Lei relacionados ao feminicídio e violência doméstica
- Visualização de dados legislativos em gráficos interativos
- Detalhamento completo de cada projeto de lei e seu histórico de tramitação
**O que está fora do escopo:**
- A plataforma não permite criar, editar ou votar em projetos de lei
- A plataforma não substitui os sistemas oficiais da Câmara e do Senado
- A plataforma não cobre proposições fora do tema de feminicídio e direitos da mulher
---

## Tecnologias
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?style=for-the-badge&logo=postgresql&logoColor=white)
![React](https://img.shields.io/badge/React-Frontend-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)

## Principais Decisões Técnicas (ADRs)

A arquitetura do Mapa L.I.L.A.S. foi desenhada com base nas seguintes premissas e decisões:
- **Separação de Responsabilidades (Desacoplamento):** O sistema adota uma arquitetura clássica dividida em um Frontend SPA puro (React/Vite) e um Backend isolado (FastAPI), comunicando-se exclusivamente via protocolo HTTP/REST.
- **Backend como Orquestrador de Dados:** Para mascarar a complexidade e a heterogeneidade das APIs do Senado e da Câmara, o backend foi construído como um agregador. Ele consome ambas as fontes, aplica o modelo classificador de IA, normaliza os esquemas de dados (status, autorias) e só então expõe um contrato de API simplificado para o Frontend.
- **Persistência Híbrida Inteligente (JSONB):** Como o governo altera as respostas de suas APIs com o passar dos anos sem aviso, usamos PostgreSQL unindo colunas relacionais clássicas para metadados com colunas tipo `JSONB` (`dados_raw`) para salvar o payload original. Isso elimina a dor de cabeça com migrações de esquema constantes quando as APIs de origem mudam estruturas não essenciais.

## Funcionalidades

### Busca por projetos de lei
* Filtro de período, partido, estado e status
* Busca Livre
* Status (apresentação, comissão, votação e sanção)

### Página de Projeto de lei
* Acesso ao histórico de tramitação
* PDF do projeto de lei
* Informações do autor
* Ementa do projeto e explicação

### Dashboard de análise
* Gráfico sobre estatísticas do tema
* Filtro de estado, partido, gênero dos autores, data, status
* Gráficos do tipo: Rosca, Pizza, Barra, Coluna e Mapa do Brasil por estado

## Documentação

- [Documentação do Backend (API e Banco de Dados)](backend/README.md)
- [Documentação do Frontend (Interface React)](frontend/README.md)
- [Git Pages (Docs completas)](https://unb-mds.github.io/2026-1-Mapa_L.I.L.A.S/)
- [Figma (Design)](https://www.figma.com/board/JerWZI6mxVFXDsDmY6ZMap/Template-MDS--c%C3%B3pia-?node-id=0-1&p=f&t=C2MuRLnn6exwREqu-0)
- [Produtividade e Scrum](https://unb-mds.github.io/2026-1-Mapa_L.I.L.A.S/scrum/)

---

## Estrutura do Projeto

O repositório está organizado seguindo um padrão monorepo para facilitar a orquestração e o desenvolvimento fullstack:

```text
2026-1-Mapa_L.I.L.A.S/
├── backend/            # Subprojeto da API em Python (FastAPI)
│   ├── app/            # Código-fonte (routers, services, schemas, models)
│   └── tests/          # Suíte de testes da API (pytest)
├── frontend/           # Subprojeto da interface de usuário em React (Vite)
│   ├── public/         # Estáticos públicos
│   └── src/            # Código-fonte (pages, components, hooks, services)
├── docs/               # Documentação técnica detalhada, atas e arquitetura
├── docker-compose.yml  # Orquestração dos containers (Front, Back e DB)
└── README.md           # Este arquivo de documentação principal
```

---

## Pré-requisitos

Para rodar este projeto localmente, você não precisa instalar o Node ou o Python na sua máquina. A única exigência é ter o Docker instalado:

* [Git](https://www.google.com/search?q=https://git-scm.com/downloads)
* [Docker](https://docs.docker.com/get-docker/)
* [Docker Compose](https://docs.docker.com/compose/install/)

---

## Passo a Passo para Rodar Localmente

### 1. Clone o repositório

Abra o terminal e baixe o código do projeto para a sua máquina:

```bash
git clone https://github.com/unb-mds/2026-1-Mapa_L.I.L.A.S.git
cd 2026-1-Mapa_L.I.L.A.S

```

### 2. Configuração de Variáveis de Ambiente (.env)
Para que o banco de dados e a conexão entre o frontend e o backend funcionem corretamente, crie um arquivo chamado `.env` dentro da pasta `backend/`.

```env
# Exemplo de configuração do banco de dados e permissão de requisições
DATABASE_URL=postgresql://postgres:suasenha@db:5432/mapa_lilas
CORS_ORIGINS=http://localhost:5173

```
 
### 3. Como Iniciar o Container

Com tudo configurado, execute o comando abaixo na raiz do projeto (onde está o arquivo `docker-compose.yml`) para baixar as dependências e subir toda a infraestrutura:

```bash
docker-compose up --build

```

---

##  Acessando a Aplicação

Quando os containers estiverem rodando e o terminal indicar que os serviços iniciaram com sucesso, abra o navegador e acesse:

*  **Frontend (Dashboard e Buscador):** [http://localhost:5173]()
*  **Backend (API Base):** [http://localhost:8000]()
*  **Documentação da API (Swagger):** [http://localhost:8000/docs]()

---

## Autores

* [@Alice Moura]()
* [@Alice Rodrigues]()
* [@Eduardo Rodrigues]()
* [@Luana Barbosa]()
* [@Rafael Schetinger]()
* [@Renan Santos]()
