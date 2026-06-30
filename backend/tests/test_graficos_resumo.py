from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
from datetime import datetime, timedelta

from app.main import app
from app.database import get_db, Base
from app.models import PlCamara, Parlamentar, AutoriaCamara, TramitacaoCamara

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

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
    
    # 1. Parlamentar SP e PL 1 (Sancionado)
    p1 = Parlamentar(id="cam_1", casa="Câmara", nome_eleitoral="Ana", sigla_partido="PT", sigla_uf="SP", sexo="F")
    pl1 = PlCamara(id=1, numero=123, ano=2024, ementa="Teste 1", data_apresentacao=datetime.now() - timedelta(days=10), descricao_situacao="Transformado em Norma Jurídica")
    aut1 = AutoriaCamara(id_pl=1, id_parlamentar="cam_1", tipo_autoria="Autor")
    tram1 = TramitacaoCamara(id_pl=1, data_tramitacao=datetime.now() - timedelta(days=2)) # 8 dias tramitando
    
    # 2. PL 2 (Não Sancionado - Arquivado)
    pl2 = PlCamara(id=2, numero=124, ano=2024, ementa="Teste 2", data_apresentacao=datetime.now() - timedelta(days=20), descricao_situacao="Arquivada")
    aut2 = AutoriaCamara(id_pl=2, id_parlamentar="cam_1", tipo_autoria="Autor")
    tram2 = TramitacaoCamara(id_pl=2, data_tramitacao=datetime.now() - timedelta(days=5)) # 15 dias tramitando, não deve entrar na média
    
    db.add_all([p1, pl1, aut1, tram1, pl2, aut2, tram2])
    db.commit()
    
    yield
    
    Base.metadata.drop_all(bind=engine)
    db.close()


client = TestClient(app)

def test_get_graficos_resumo():
    response = client.get("/api/graficos/resumo")
    assert response.status_code == 200
    
    data = response.json()
    assert "tempo_medio_tramitacao" in data
    assert "top_estados" in data
    assert "parlamentares_ativos" in data
    
    # Tracer bullet checks
    # Só o PL 1 deve ser considerado no tempo médio (8 dias), PL 2 (15 dias) é ignorado
    assert data["tempo_medio_tramitacao"]["dias"] == 8
    assert "variacao_percentual" not in data["tempo_medio_tramitacao"]
    assert "tendencia" not in data["tempo_medio_tramitacao"]
    
    assert len(data["top_estados"]) == 1
    assert data["top_estados"][0]["uf"] == "SP"
    
    assert len(data["parlamentares_ativos"]) == 1
    assert data["parlamentares_ativos"][0]["nome"] == "Ana"
    assert data["parlamentares_ativos"][0]["descricao"] == "Deputada Federal - PT"
