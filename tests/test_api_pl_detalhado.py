from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from app.main import app
from app.database import get_db

client = TestClient(app)

def override_get_db():
    db = MagicMock()
    # Para o teste_not_found
    db.execute.return_value.fetchone.return_value = None
    yield db

app.dependency_overrides[get_db] = override_get_db

def test_get_pl_detalhado_camara():
    # Vamos mockar o Session do SQLAlchemy diretamente no override_get_db local
    mock_db = MagicMock()
    # Simular o retorno da query principal
    mock_row = MagicMock()
    mock_row.id = 1
    mock_row.numero = "996"
    mock_row.ano = 2023
    mock_row.casa = "Câmara dos Deputados"
    mock_row.ementa = "Ementa teste"
    mock_row.dados_raw = {
        "urlInteiroTeor": "http://camara.leg.br/pdf/1",
        "keywords": "Tema1, Tema2",
    }
    mock_row.status_normalizado = "aprovado"
    mock_row.descricao_situacao = "Transformado em Norma Jurídica"
    mock_row.autor_nome = "Teresa Leitão"
    mock_row.autor_partido = "PT"
    mock_row.autor_uf = "PE"
    
    mock_db.execute.return_value.fetchone.return_value = mock_row
    
    # Mock para autorias (se tiver queries adicionais) e histórico
    mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
    
    app.dependency_overrides[get_db] = lambda: mock_db
    
    response = client.get("/api/projetos-de-lei/camara/996/2023")
    # O teste falha aqui (404) porque a rota ainda não foi criada, é o RED esperado
    assert response.status_code == 200

def test_get_pl_detalhado_senado():
    mock_db = MagicMock()
    mock_row = MagicMock()
    mock_row.numero = "21"
    mock_row.ano = 2020
    mock_row.casa = "Senado Federal"
    mock_row.dados_raw = {
        "documento": {"url": "http://senado.leg.br/pdf/21"},
        "indexacao": "TemaA, TemaB",
        "situacaoAtual": "PREJUDICADA"
    }
    mock_db.execute.return_value.fetchone.return_value = mock_row
    app.dependency_overrides[get_db] = lambda: mock_db
    
    response = client.get("/api/projetos-de-lei/senado/21/2020")
    assert response.status_code == 200

def test_get_pl_detalhado_not_found():
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None
    app.dependency_overrides[get_db] = lambda: mock_db
    
    response = client.get("/api/projetos-de-lei/camara/999999/2099")
    assert response.status_code == 404
