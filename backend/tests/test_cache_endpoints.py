"""
Testes de cache para os endpoints /stats, /filtros e /projetos-de-lei.

Cada teste verifica o comportamento observável via interface pública (HTTP):
a segunda chamada ao mesmo endpoint deve retornar o mesmo resultado
sem consultar o banco de dados novamente.
"""
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from datetime import datetime, timedelta

from app.main import app
from app.database import get_db, Base
from app.models import PlCamara, Parlamentar, AutoriaCamara, TramitacaoCamara


# ── Test DB Setup ──────────────────────────────────────────────
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_cache.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def set_dependency_overrides():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    p1 = Parlamentar(
        id="cam_cache_1", casa="Câmara", nome_eleitoral="CacheTest",
        sigla_partido="PT", sigla_uf="SP", sexo="F"
    )
    pl1 = PlCamara(
        id=9001, numero=9001, ano=2024, ementa="PL para teste de cache",
        data_apresentacao=datetime.now() - timedelta(days=10),
        descricao_situacao="Transformado em Norma Jurídica"
    )
    aut1 = AutoriaCamara(
        id_pl=9001, id_parlamentar="cam_cache_1", tipo_autoria="Autor"
    )
    tram1 = TramitacaoCamara(
        id_pl=9001, data_tramitacao=datetime.now() - timedelta(days=2)
    )
    pl2 = PlCamara(
        id=9002, numero=9002, ano=2024, ementa="PL 2 cache",
        data_apresentacao=datetime.now() - timedelta(days=5),
        descricao_situacao="Arquivada"
    )
    aut2 = AutoriaCamara(
        id_pl=9002, id_parlamentar="cam_cache_1", tipo_autoria="Autor"
    )

    db.add_all([p1, pl1, aut1, tram1, pl2, aut2])
    db.commit()

    yield

    Base.metadata.drop_all(bind=engine)
    db.close()


@pytest.fixture(autouse=True)
def clear_caches():
    """Limpa todos os caches antes de cada teste para isolamento."""
    from app.cache import (
        cache_stats, cache_filtros, cache_projetos,
        cache_resumo, cache_distribuicao,
    )
    cache_stats.clear()
    cache_filtros.clear()
    cache_projetos.clear()
    cache_resumo.clear()
    cache_distribuicao.clear()
    yield


client = TestClient(app)


# ── Slice 1: /stats cache ─────────────────────────────────────
def test_stats_returns_cached_response():
    """O endpoint /stats deve retornar o mesmo resultado na segunda
    chamada, usando cache em vez de consultar o banco novamente."""
    from app.cache import cache_stats

    # Primeira chamada: cache vazio → consulta o banco
    resp1 = client.get("/api/projetos-de-lei/stats")
    assert resp1.status_code == 200
    data1 = resp1.json()

    # Verifica que o resultado tem a estrutura esperada
    assert "total" in data1
    assert "em_tramitacao" in data1
    assert "aprovados" in data1
    assert "arquivados" in data1

    # Cache deve ter sido populado
    assert len(cache_stats) == 1

    # Segunda chamada: deve retornar o mesmo resultado (do cache)
    resp2 = client.get("/api/projetos-de-lei/stats")
    assert resp2.status_code == 200
    assert resp2.json() == data1


# ── Slice 2: /filtros cache ───────────────────────────────────
def test_filtros_returns_cached_response():
    """O endpoint /filtros deve retornar o mesmo resultado na segunda
    chamada, usando cache em vez de consultar o banco novamente."""
    from app.cache import cache_filtros

    resp1 = client.get("/api/projetos-de-lei/filtros")
    assert resp1.status_code == 200
    data1 = resp1.json()

    assert "partidos" in data1
    assert "ufs" in data1
    assert "anos" in data1

    # Cache deve ter sido populado
    assert len(cache_filtros) == 1

    # Segunda chamada: deve retornar o mesmo resultado (do cache)
    resp2 = client.get("/api/projetos-de-lei/filtros")
    assert resp2.status_code == 200
    assert resp2.json() == data1


# ── Slice 3: /projetos-de-lei cache (sem filtros) ─────────────
def test_projetos_sem_filtros_returns_cached_response():
    """A listagem de projetos sem filtros (page=1, per_page=10) deve
    ser cacheada na segunda chamada."""
    from app.cache import cache_projetos

    resp1 = client.get("/api/projetos-de-lei?page=1&per_page=10&ordenar=recentes")
    assert resp1.status_code == 200
    data1 = resp1.json()

    assert "projetos" in data1
    assert "total" in data1

    # Cache deve ter sido populado com chave recentes_all_10
    assert len(cache_projetos) == 1

    # Segunda chamada: deve retornar o mesmo resultado (do cache)
    resp2 = client.get("/api/projetos-de-lei?page=1&per_page=10&ordenar=recentes")
    assert resp2.status_code == 200
    assert resp2.json() == data1


def test_projetos_com_filtro_nao_usa_cache():
    """A listagem de projetos COM filtros de conteúdo NÃO deve ser cacheada."""
    from app.cache import cache_projetos

    # Chamada com filtro de keyword
    resp1 = client.get("/api/projetos-de-lei?keyword=cache&page=1&per_page=10")
    assert resp1.status_code == 200

    # Cache NÃO deve ter sido populado
    assert len(cache_projetos) == 0


def test_projetos_com_status_filter_usa_cache():
    """A listagem com filtro de status (sem outros filtros) deve ser cacheada."""
    from app.cache import cache_projetos

    resp1 = client.get("/api/projetos-de-lei?page=1&per_page=10&ordenar=recentes&status=aprovado")
    assert resp1.status_code == 200

    # Cache deve ter sido populado com chave recentes_aprovado_10
    assert len(cache_projetos) == 1

    resp2 = client.get("/api/projetos-de-lei?page=1&per_page=10&ordenar=recentes&status=aprovado")
    assert resp2.status_code == 200
    assert resp2.json() == resp1.json()


# ── Slice 4: Ordenação de rotas ───────────────────────────────
def test_stats_route_not_intercepted_by_detail_route():
    """O endpoint /stats não deve ser interceptado pela rota
    /{casa}/{numero}/{ano}. Deve retornar dados de stats, não um erro."""
    resp = client.get("/api/projetos-de-lei/stats")
    assert resp.status_code == 200
    data = resp.json()

    # Deve ter a estrutura de stats, não de detalhe de projeto
    assert "total" in data
    assert "em_tramitacao" in data

    # NÃO deve ter campos de detalhe de projeto
    assert "ementa" not in data
    assert "historico" not in data


def test_filtros_route_not_intercepted_by_detail_route():
    """O endpoint /filtros não deve ser interceptado pela rota
    /{casa}/{numero}/{ano}. Deve retornar dados de filtros, não um erro."""
    resp = client.get("/api/projetos-de-lei/filtros")
    assert resp.status_code == 200
    data = resp.json()

    assert "partidos" in data
    assert "ufs" in data
    assert "anos" in data


# ── Slice 5: Migração graficos.py → app.cache ─────────────────
def test_graficos_resumo_works_after_migration():
    """O endpoint /graficos/resumo deve continuar funcionando
    após a migração dos caches para app.cache."""
    from app.cache import cache_resumo

    resp1 = client.get("/api/graficos/resumo")
    assert resp1.status_code == 200
    data1 = resp1.json()

    assert "tempo_medio_tramitacao" in data1
    assert "top_estados" in data1
    assert "parlamentares_ativos" in data1

    # Cache deve ter sido populado
    assert len(cache_resumo) == 1

    # Segunda chamada retorna do cache
    resp2 = client.get("/api/graficos/resumo")
    assert resp2.status_code == 200
    assert resp2.json() == data1


def test_graficos_distribuicao_works_after_migration():
    """O endpoint /graficos/distribuicao deve continuar funcionando
    após a migração dos caches para app.cache."""
    from app.cache import cache_distribuicao

    resp1 = client.get("/api/graficos/distribuicao?comparar_por=partido")
    assert resp1.status_code == 200
    data1 = resp1.json()

    assert "comparar_por" in data1
    assert data1["comparar_por"] == "partido"

    # Cache deve ter sido populado
    assert len(cache_distribuicao) == 1

    # Segunda chamada retorna do cache
    resp2 = client.get("/api/graficos/distribuicao?comparar_por=partido")
    assert resp2.status_code == 200
    assert resp2.json() == data1




