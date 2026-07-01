# Integração e Entrega Contínuas (CI/CD)

Para manter a estabilidade, padronização e integridade de todas as entregas no repositório do L.I.L.A.S., implementamos uma esteira de **CI/CD** altamente autônoma via GitHub Actions.

A ideia fundamental é: **Nenhum código quebra a branch principal, e toda aprovação se torna uma entrega.**

Para que uma funcionalidade vá para produção (ou até mesmo seja mergeada na `main`), ela precisa passar obrigatoriamente pelos nossos pipelines de Integração Contínua (CI) e, em seguida, é distribuída pelos nossos pipelines de Entrega Contínua (CD).

## Nossos Workflows de CI (Integração)

### 1. Testes Automatizados e Docker (`ci-docker.yml`)
Todo e qualquer Pull Request obriga a execução da suíte completa do `pytest` dentro do ambiente Docker efêmero, reproduzindo a arquitetura exata de produção. 
* **O que acontece se falhar:** Se um único teste falhar (por exemplo, um endpoint retornou 500 em vez de 200), o código é imediatamente bloqueado e o merge é impossibilitado.

### 2. Padronização Estética e Qualidade (`lint.yml`)
Sempre que alguém tenta modificar o projeto, o Actions faz a varredura do código modificado usando nossas ferramentas (como Flake8 e ESLint).
* **O que acontece se falhar:** Caso haja quebras de linha irregulares, o pipeline quebra. Isso blinda o projeto contra o acúmulo de novos *Code Smells*.

---

## Nossos Workflows de CD (Deploy Automático)

A fase de *Continuous Deployment* (CD) ocorre no exato momento em que um Pull Request é aprovado e as mudanças são unificadas na branch `main`. A equipe não precisa executar comandos manuais para subir o projeto no servidor.

### 3. Deploys do Ecossistema (`deploy-backend.yml` e `deploy-frontend.yml`)
* **Gatilho (Trigger):** Ativados automaticamente a cada "push" na branch `main`.
* **Frontend:** A pipeline notifica a Vercel para reconstruir os assets estáticos em React/Vite. Em poucos segundos, o novo dashboard é espalhado pela Edge Network global da Vercel.
* **Backend:** Da mesma forma, a API em FastAPI é provisionada como Serverless Functions. O banco de dados (Neon) já está conectado via variáveis de ambiente configuradas na plataforma.
* **Resultado:** O deploy é imediato, invisível aos usuários finais, e livre de indisponibilidades ("zero downtime deployment").

---

## Outros Workflows de Backoffice
A esteira também orquestra rotinas invisíveis de operação diária:
* **`data-ingestion.yml`:** A pipeline autônoma que captura dados do governo em horários agendados (CRON).
* **`static.yml` / `scrum metrics.yml`:** Pipelines que fazem o build automático da documentação atual do MkDocs e atualizam as planilhas de métricas do nosso ciclo Scrum.
