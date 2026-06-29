# 🚀 Release Final - Mapa L.I.L.A.S

**Data: Julho de 2026**

---

## ✅ O que foi entregue nesta Release

Fechamos o escopo final do projeto integrando a raspagem de dados do legislativo ao ecossistema do frontend. O foco dessa reta final foi a automação de pipelines, tratamento de dados complexos e análise da qualidade do código.

### 🧩 Funcionalidades e Engenharia de Dados

**🧠 Pipelines de Captura de Dados e PNL**
* **Mapeamento por Palavras-Chave:** Desenvolvimento de pipelines para capturar projetos de lei na Câmara e no Senado de forma dinâmica, filtrando os termos do escopo.
* **Infraestrutura de Processamento de Linguagem Natural (PLN):** Criação de rotinas de processamento de texto e testes unitários para classificar e tratar as proposições capturadas.
* **Parsers e Mocking:** Implementação de lógica de prompts e parsers com tratamento de exceções, além de um modo Mock para simular os dados em ambiente de desenvolvimento.

**📊 Frontend e Endpoints da API**
* **Endpoints de Agregação:** Criação do endpoint `/api/graficos/resumo` para alimentar os gráficos do frontend.
* **Dashboards Visuais:** Telas de gráficos interativos (Pizza, Rosca, Barras e Mapa do Brasil por estado) puxando os dados reais da API.
* **Página de Detalhamento:** Unificação da tela de detalhes dos Projetos de Lei, exibindo ementa, autor, histórico de tramitação e o link do PDF original.

---

## ⚙️ DevOps e Infraestrutura (CI/CD)

* **Containers e Orquestração:** Dockerfiles e `docker-compose.yml` configurados para rodar a aplicação inteira (Front, Back e PostgreSQL) em paralelo.
* **Automação da Ingestão de Dados:** Configuração de um cronograma via GitHub Actions para rodar o script de raspagem de dados de segunda a sexta-feira às 23:57 BRT.
* **Testes Automatizados:** Implementação de testes de integração front-back rodando isolados dentro do ambiente Docker.
* **GitHub Pages:** Deploy automatizado para atualizar o site da documentação (MkDocs) e o painel de métricas do Scrum a cada alteração na branch principal.

---

## 📊 Indicadores de Qualidade de Código (SonarQube)

Como parte dos critérios de validação, rodámos a ferramenta **SonarQube** para mapear a estrutura técnica sobre as **15 mil linhas de código** geradas no projeto. Os resultados servem como mapeamento preventivo para futuras iterações do software:

* **Manutenibilidade (Nota A):** O projeto atingiu a classificação máxima em legibilidade e organização. Os apontamentos de *Code Smells* referem-se a melhorias estéticas simples (como remoção de variáveis declaradas e não utilizadas), o que simplifica futuras evoluções do sistema.
* **Confiabilidade e Segurança:** A ferramenta catalogou os pontos de atenção lógicos e estruturais padrão para o ecossistema FastAPI/React, a maioria associada à parametrização e ao isolamento de variáveis de configuração em ambiente de desenvolvimento local (`.env`). Isso gera um plano de ação claro para os ajustes necessários antes de um deploy em produção.
* **Taxa de Duplicação (31,5%):** Identificação de trechos repetidos entre arquivos, servindo como guia para a centralização de funções e criação de componentes globais reutilizáveis nas próximas fases.

---

## 🛠️ Stack Tecnológica Utilizada

* **Frontend:** React + Vite + TailwindCSS
* **Backend:** Python + FastAPI + Módulos de PNL
* **Banco de Dados:** PostgreSQL (armazenamento de dados brutos usando tipo `JSONB`)
* **Infraestrutura / Qualidade:** Docker + GitHub Actions + MkDocs + SonarQube

---

## 👥 Integrantes
* Alice Moura
* Alice Rodrigues
* Eduardo Rodrigues
* Luana Barbosa
* Rafael Schetinger
* Renan Santos