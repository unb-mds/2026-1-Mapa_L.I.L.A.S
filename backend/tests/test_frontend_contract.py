import os
import json
import pytest
from app.schemas.graficos import ResumoResponse
from app.schemas.projeto import StatsResponse, ProjetosResponse, FiltrosResponse

FRONTEND_FIXTURES_DIR = os.path.join(
    os.path.dirname(__file__), 
    "..", "..", "frontend", "cypress", "fixtures"
)

def load_fixture(filename: str) -> dict:
    filepath = os.path.join(FRONTEND_FIXTURES_DIR, filename)
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def test_contract_graficos_resumo():
    """
    Garante que o mock 'graficos_resumo.json' consumido pelo Frontend
    passa pela tipagem e chaves esperadas pelo Backend (ResumoResponse).
    """
    data = load_fixture("graficos_resumo.json")
    # Se o mock não bater com o esquema, Pydantic lançará ValidationError
    model = ResumoResponse.model_validate(data)
    assert model.tempo_medio_tramitacao.dias == 120

def test_contract_stats():
    """
    Garante que o mock 'stats.json' consumido pelo Frontend
    passa pela tipagem e chaves esperadas pelo Backend (StatsResponse).
    """
    data = load_fixture("stats.json")
    model = StatsResponse.model_validate(data)
    assert model.total > 0

def test_contract_projetos_lista():
    """
    Garante que o mock 'projetos_lista.json' consumido pelo Frontend
    passa pela tipagem e chaves esperadas pelo Backend (ProjetosResponse).
    """
    data = load_fixture("projetos_lista.json")
    model = ProjetosResponse.model_validate(data)
    assert model.total == 1
    assert len(model.projetos) > 0

def test_contract_projetos_filtros():
    """
    Garante que o mock 'projetos_filtros.json' consumido pelo Frontend
    passa pela tipagem e chaves esperadas pelo Backend (FiltrosResponse).
    """
    data = load_fixture("projetos_filtros.json")
    model = FiltrosResponse.model_validate(data)
    assert "PT" in model.partidos
