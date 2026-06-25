from fastapi import FastAPI
from app.routers import projeto, graficos
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app = FastAPI(title="L.I.L.A.S. API", version="2.0")

# AC-12: Configuração de CORS (ajuste os origins conforme necessário para o React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Mude para o domínio do front end em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra as rotas que criamos
app.include_router(projeto.router)
# Registra as rotas de gráficos usadas pelo Dashboard Detalhado.
app.include_router(graficos.router)


@app.get("/")
def read_root():
    return {"status": "API L.I.L.A.S. Online"}
