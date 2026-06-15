from unittest.mock import patch, MagicMock
from app.services import collector

@patch("app.services.collector.camara_client")
@patch("app.services.collector.upsert_pl_camara")
@patch("app.services.collector.upsert_autores_camara")
@patch("app.services.collector.upsert_tramitacoes_camara")
def test_coletar_camara_mescla_detalhes_no_raw(
    mock_upsert_tramitacoes,
    mock_upsert_autores,
    mock_upsert_pl,
    mock_camara_client
):
    """
    TDD RED: Garantir que coletar_camara mescla o item_raw com detalhe_raw
    antes de passar para o upsert_pl_camara (como argumento dados_originais).
    """
    # 1. Configurar Mocks
    # Limitar o loop do SIGLAS_TIPO e PALAVRAS_CHAVE para simplificar
    collector.camara_client.SIGLAS_TIPO = ["PL"]
    collector.camara_client.PALAVRAS_CHAVE = ["feminicídio"]
    
    mock_session = MagicMock()
    
    # Simular 1 PL retornado pela listagem básica
    mock_camara_client.listar_proposicoes.return_value = [
        {"id": 123, "ementa": "Item Raw Ementa"}
    ]
    # Simular ausência de autores do senado
    mock_camara_client.buscar_autores.return_value = [{"nome": "Deputada Teste"}]
    # Simular os detalhes sendo retornados
    mock_camara_client.buscar_detalhe.return_value = {
        "urlInteiroTeor": "http://camara.gov/pdf/123",
        "keywords": "Feminicídio, Teste"
    }
    
    # Fazer o upsert retornar um ID válido para continuar o fluxo
    mock_upsert_pl.return_value = 123

    # 2. Executar
    collector.coletar_camara(mock_session, numdias=1)
    
    # 3. Asserções
    # upsert_pl_camara(session, item_raw, detalhe_raw, dados_originais)
    assert mock_upsert_pl.called
    args, kwargs = mock_upsert_pl.call_args
    dados_originais_passados = args[3]
    
    # Esperamos que o dicionário passado contenha tanto a chave do item_raw quanto do detalhe_raw
    assert "ementa" in dados_originais_passados, "A chave 'ementa' do item_raw sumiu"
    assert "urlInteiroTeor" in dados_originais_passados, "A chave 'urlInteiroTeor' do detalhe_raw não foi mesclada!"
    assert dados_originais_passados["urlInteiroTeor"] == "http://camara.gov/pdf/123"

@patch("app.services.collector.senado_client")
@patch("app.services.collector.upsert_pl_senado")
@patch("app.services.collector.upsert_autores_senado")
@patch("app.services.collector.upsert_tramitacoes_senado")
def test_coletar_senado_mescla_detalhes_no_raw(
    mock_upsert_tramitacoes,
    mock_upsert_autores,
    mock_upsert_pl,
    mock_senado_client
):
    """
    TDD RED: Garantir que coletar_senado puxa o detalhe ANTES do upsert principal
    e passa a mescla de (item_raw + detalhe_raw) para o upsert_pl_senado.
    """
    # 1. Configurar Mocks
    collector.senado_client.SIGLAS_TIPO = ["PL"]
    collector.senado_client.PALAVRAS_CHAVE = ["feminicídio"]
    
    mock_session = MagicMock()
    
    # Simular 1 PL retornado
    mock_senado_client.pesquisar_materias.return_value = [
        {"id": 456, "identificacao": "PL 123/2023", "ementa": "Item Raw Senado"}
    ]
    # Simular os detalhes
    mock_senado_client.buscar_detalhe.return_value = {
        "documento": {"url": "http://senado.gov/pdf/456"},
        "situacaoAtual": "Aprovada"
    }
    
    mock_upsert_pl.return_value = 456

    # 2. Executar
    collector.coletar_senado(mock_session, numdias=1)
    
    # 3. Asserções
    # upsert_pl_senado(session, item_raw, dados_originais)
    assert mock_upsert_pl.called
    args, kwargs = mock_upsert_pl.call_args
    dados_originais_passados = args[2]
    
    assert "ementa" in dados_originais_passados
    assert "documento" in dados_originais_passados, "Detalhes do Senado não foram mesclados no upsert_pl_senado"
    assert dados_originais_passados["documento"]["url"] == "http://senado.gov/pdf/456"
