# Frontend - Mapa L.I.L.A.S.

Este diretório contém a interface de usuário (SPA) do projeto Mapa L.I.L.A.S., uma plataforma para busca, acompanhamento e visualização de proposições legislativas sobre feminicídio e direitos da mulher.

## Funcionalidades

- **Busca Semântica e Filtros:** Busca por proposições legislativas utilizando palavras-chave, filtros por status, datas e tipo de documento.
- **Cards de Proposições (PLCard):** Exibição padronizada das proposições (Projetos de Lei, PECs, etc.) mostrando o status normalizado (ex: `em_tramitacao`, `aprovado`) e a autoria principal (parlamentar autor).
- **Visualização de Dados:** Gráficos analíticos e informativos utilizando a biblioteca Recharts.
- **Integração com Backend:** Comunicação HTTP/REST com a API em FastAPI, que fornece os dados já normalizados e padronizados das APIs públicas da Câmara e do Senado.

## 🛠️ Stack Tecnológica e Decisões (ADRs)

- **React 19:** Escolhido por sua forte componentização e ecossistema maduro para Single Page Applications (SPAs).
- **Vite:** Utilizado como bundler de build tool, sendo extremamente rápido e otimizado, proporcionando um ambiente de desenvolvimento ágil com Hot-Module Replacement (HMR) ultrarrápido.
- **Tailwind CSS v4:** Framework de estilização baseado em classes utilitárias. Foi escolhido por facilitar a criação de componentes padronizados e responsivos (Atomic Components), sem a necessidade de manter arquivos CSS complexos.
- **React Router DOM v7:** Utilizado para roteamento dinâmico no client-side, permitindo navegação fluída sem recarregar a página inteira.
- **Recharts v3:** Biblioteca declarativa focada em React para renderização de gráficos em SVG. Fundamental para montar dashboards analíticos sobre a evolução dos PLs.

---

## Estrutura de Pastas

```text
frontend/
├── public/               # Arquivos estáticos não processados pelo bundler
├── src/                  # Código-fonte principal da aplicação
│   ├── assets/           # Imagens, fontes e recursos visuais
│   ├── components/       # Componentes React reutilizáveis (Atomic UI)
│   ├── hooks/            # Custom hooks do React para lógica isolada
│   ├── mocks/            # Dados estáticos simulados para testes e fallback
│   ├── pages/            # Componentes estruturais de páginas (Roteamento)
│   ├── services/         # Módulos de comunicação HTTP com a API do backend
│   ├── App.jsx           # Componente raiz estrutural do React
│   └── main.jsx          # Ponto de entrada e injeção do React no DOM
├── index.html            # Template HTML principal servido ao navegador
├── package.json          # Configuração de dependências e scripts do NPM
└── vite.config.js        # Configuração do compilador/bundler Vite
```

---

## Configuração do Ambiente Local

### Pré-requisitos
- **Node.js** (versão recomendada >= 20.x)
- **npm** (padrão de gerencimento de pacotes do projeto)

### 1. Instalar Dependências

No terminal, dentro da pasta `frontend/`, execute:

```bash
npm install
```

### 2. Variáveis de Ambiente

Certifique-se de configurar o seu `.env` ou `.env.local` na raiz da pasta `frontend/`, especialmente a variável que aponta para a URL do Backend (ex: `VITE_API_URL=http://localhost:8000`).

### 3. Rodando o Servidor de Desenvolvimento

Para iniciar o ambiente local do Vite:

```bash
npm run dev
```

A aplicação estará acessível em: [http://localhost:5173](http://localhost:5173)

---

## Build para Produção

Para compilar o código em arquivos estáticos minificados e otimizados:

```bash
npm run build
```

Os arquivos prontos para deploy (HTML, JS, CSS gerados pelo bundler) ficarão disponíveis na pasta `dist/`. Para rodar e visualizar como o build de produção se comporta localmente:

```bash
npm run preview
```

---

## Uso com Docker

O frontend está incluso na infraestrutura Docker do projeto. Caso deseje rodar a aplicação junto de todo o ecossistema (Backend + Banco de Dados), volte para a pasta raiz do repositório (uma pasta acima do `/frontend`) e rode:

```bash
docker-compose up -d --build frontend
```

O contêiner do frontend cuidará da instalação, e a porta `5173` continuará sendo mapeada para a sua máquina hospedeira.
