import pytest
from unittest.mock import patch, MagicMock
from app.services.collector import coletar_camara, coletar_senado
from app.services import camara_client, senado_client

@patch('app.services.collector.camara_client.listar_proposicoes')
@patch('app.services.collector.get_dynamic_keywords')
def test_coletar_camara_uses_dynamic_keywords(mock_get_dynamic, mock_listar):
    """
    Verifica se o coletor da câmara obtém a lista de palavras-chave da IA
    e faz a busca usando essa nova lista em vez da estática.
    """
    mock_session = MagicMock()
    # Forçamos a IA a retornar palavras diferentes das originais
    mock_get_dynamic.return_value = ["termo_ia_1", "termo_ia_2"]
    
    # Retorna vazio para a iteração ser rápida (não processa PLs de verdade)
    mock_listar.return_value = iter([])
    
    # Executa
    coletar_camara(mock_session, numdias=1)
    
    # 1. Checa se o serviço NLP foi chamado usando as sementes locais como base
    mock_get_dynamic.assert_called_once_with(camara_client.PALAVRAS_CHAVE)
    
    # 2. Checa se as chamadas de API feitas usaram as palavras da IA
    # Siglas padrão: ['PL', 'PLP'] * 2 palavras = 4 chamadas
    assert mock_listar.call_count == len(camara_client.SIGLAS_TIPO) * 2
    
    # Extrai o segundo argumento (keyword) de cada chamada a listar_proposicoes
    keywords_usadas = [call.args[1] for call in mock_listar.call_args_list]
    
    assert "termo_ia_1" in keywords_usadas
    assert "termo_ia_2" in keywords_usadas
    
    # Confirma que as palavras estáticas não foram usadas se a IA retornou outra coisa
    assert camara_client.PALAVRAS_CHAVE[0] not in keywords_usadas

@patch('app.services.collector.senado_client.pesquisar_materias')
@patch('app.services.collector.get_dynamic_keywords')
def test_coletar_senado_uses_dynamic_keywords(mock_get_dynamic, mock_pesquisar):
    mock_session = MagicMock()
    mock_get_dynamic.return_value = ["termo_ia_1", "termo_ia_2"]
    
    mock_pesquisar.return_value = []
    
    coletar_senado(mock_session, numdias=1)
    
    mock_get_dynamic.assert_called_once_with(senado_client.PALAVRAS_CHAVE)
    
    # Siglas padrão (3) * 2 palavras da IA = 6 chamadas
    assert mock_pesquisar.call_count == len(senado_client.SIGLAS_TIPO) * 2
    
    keywords_usadas = [call.kwargs.get("keyword") for call in mock_pesquisar.call_args_list]
    
    assert "termo_ia_1" in keywords_usadas
    assert "termo_ia_2" in keywords_usadas

