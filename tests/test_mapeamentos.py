import pytest
from app.routers.projeto import mapear_estagio_atual_camara, mapear_estagio_atual_senado, extrair_temas

def test_mapear_estagio_atual_senado():
    assert mapear_estagio_atual_senado("AGUARDANDO DESPACHO") == "apresentacao"
    assert mapear_estagio_atual_senado("AGUARDANDO DESIGNAÇÃO DO RELATOR") == "comissao"
    assert mapear_estagio_atual_senado("REMETIDA À CÂMARA DOS DEPUTADOS") == "votacao"
    assert mapear_estagio_atual_senado("TRANSFORMADA EM NORMA JURÍDICA") == "sancao"
    assert mapear_estagio_atual_senado("PREJUDICADA") == "rejeitado"
    assert mapear_estagio_atual_senado(None) == "rejeitado"
    # Fallback
    assert mapear_estagio_atual_senado("STATUS DESCONHECIDO") == "apresentacao"

def test_mapear_estagio_atual_camara():
    assert mapear_estagio_atual_camara("Aguardando Despacho do Presidente da Câmara dos Deputados (Análise)") == "apresentacao"
    assert mapear_estagio_atual_camara("Aguardando Parecer") == "comissao"
    assert mapear_estagio_atual_camara("Aguardando Deliberação") == "votacao"
    assert mapear_estagio_atual_camara("Transformado em Norma Jurídica") == "sancao"
    assert mapear_estagio_atual_camara("Arquivada") == "rejeitado"
    assert mapear_estagio_atual_camara(None) == "rejeitado"
    # Fallback
    assert mapear_estagio_atual_camara("Status Desconhecido") == "apresentacao"

def test_extrair_temas():
    # Câmara format
    assert extrair_temas("Feminicídio, Violência contra a mulher, Penal") == ["Feminicídio", "Violência contra a mulher", "Penal"]
    # Senado format
    assert extrair_temas(" DIREITO ,  MULHER ,  PROTEÇÃO .") == ["DIREITO", "MULHER", "PROTEÇÃO"]
    assert extrair_temas(None) == []
    assert extrair_temas("") == []
