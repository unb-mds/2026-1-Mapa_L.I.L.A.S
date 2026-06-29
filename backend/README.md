# Backend - Mapa L.I.L.A.S.

Este diretório contém o código-fonte da API (FastAPI) do projeto Mapa L.I.L.A.S. Siga as instruções abaixo para configurar o ambiente de desenvolvimento, rodar a aplicação localmente, executar os testes e utilizar o Docker.

## Pré-requisitos

- Python 3.10+
- (Opcional) Docker e Docker Compose

---

## Configuração do Ambiente Local

Recomendamos o uso de ambiente virtual (`.venv`) para isolar as dependências do projeto.

### 1. Criar e Ativar o Ambiente Virtual

No terminal, dentro da pasta `backend/`, execute:

**No Windows:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**No Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

*(Para desativar o ambiente, basta rodar `deactivate`)*

### 2. Instalar Dependências

Com o ambiente virtual ativado, instale as dependências principais e as de desenvolvimento (para rodar os testes, linting, etc.):

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Variáveis de Ambiente

O projeto depende de variáveis de ambiente.
Verifique se o arquivo `.env` (ou `.env.local`) existe na raiz do `backend/` com as variáveis necessárias configuradas (ex: credenciais do banco de dados).

---

## Rodando a Aplicação Localmente

Para iniciar a API localmente (modo de desenvolvimento com hot-reload), execute o servidor com o Uvicorn:

```bash
uvicorn app.main:app --reload
```
*(Caso o ponto de entrada da sua aplicação seja diferente, ajuste `app.main` conforme o nome do arquivo e instância da sua aplicação FastAPI)*

A aplicação estará acessível em: [http://localhost:8000](http://localhost:8000)
A documentação interativa da API (Swagger UI) pode ser acessada em: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Rodando os Testes

O projeto utiliza o `pytest` para testes automatizados. Para executá-los, certifique-se de que as dependências de desenvolvimento estão instaladas e rode:

```bash
pytest
```
Para rodar os testes com informações mais detalhadas:
```bash
pytest -v
```

---

## Utilizando Docker

Se preferir não instalar as dependências localmente na sua máquina, você pode subir o banco de dados e o backend simultaneamente usando o Docker Compose disponível na raiz do projeto.

Volte para a pasta raiz do repositório (uma pasta acima de `backend/`) e execute:

```bash
docker-compose up -d --build db backend
```

- O serviço `db` (PostgreSQL) subirá na porta padrão (5432).
- O serviço `backend` será exposto na porta **8000** e já irá se conectar automaticamente ao banco de dados.

Para visualizar os logs da API rodando via Docker:
```bash
docker-compose logs -f backend
```
Para parar os contêineres:
```bash
docker-compose down
```
