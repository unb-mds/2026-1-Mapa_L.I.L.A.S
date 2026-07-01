"""
app/services/senado_client.py
"""

import logging
from typing import Any, Optional
import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://legis.senado.leg.br/dadosabertos"
TIMEOUT = 30

PALAVRAS_CHAVE = [
    "feminicídio",
    "violência doméstica",
    "direitos da mulher",
]

# Adicionado PLS como você pediu
SIGLAS_TIPO = ["PL", "PLP", "PLS"]

_cache_senadores = {}

def _get(path: str, params: Optional[dict] = None) -> Any:
    url = f"{BASE_URL}/{path.lstrip('/')}"
    headers = {"Accept": "application/json"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as exc:
        logger.warning("Senado API indisponível [%s]: %s", url, exc)
        return None

def pesquisar_materias(
    keyword: str,
    sigla_tipo: str,
    ano_inicial: Optional[int] = None,
    numdias: Optional[int] = None,
) -> list[dict[str, Any]]:
    
    # Usando exatamente os parâmetros da sua URL de sucesso
    params: dict[str, Any] = {
        "sigla": sigla_tipo,
        "termo": keyword,
        "v": 1
    }
    
    if ano_inicial:
        params["dataInicioApresentacao"] = f"{ano_inicial}-01-01"
        
    if numdias:
        params["numdias"] = numdias

    raw_response = _get("/processo", params)
    
    if not raw_response:
        return []

    from app.schemas.external_api import SenadoProposicaoSchema

    # O SEGREDO: com v=1, a API retorna uma LISTA direta, e não um DICIONÁRIO.
    if isinstance(raw_response, list):
        for item in raw_response:
            SenadoProposicaoSchema.model_validate(item)
        return raw_response
        
    # Fallback de segurança (caso a API mude de ideia e mande um dict)
    if isinstance(raw_response, dict):
        processos = raw_response.get("Processos", raw_response.get("ListaProcessos", []))
        if isinstance(processos, dict):
            processos = [processos]
            
        for item in processos:
            SenadoProposicaoSchema.model_validate(item)
        return processos

    return []

def buscar_detalhe(cod_materia: int) -> Optional[dict[str, Any]]:
    return _get(f"/processo/{cod_materia}")

def buscar_movimentacoes(cod_materia: int) -> Optional[dict[str, Any]]:
    return _get(f"/processo/{cod_materia}/movimentacoes")

def buscar_senador(cod_parlamentar: int) -> Optional[dict[str, Any]]:
    cod_str = str(cod_parlamentar)
    if cod_str in _cache_senadores:
        return _cache_senadores[cod_str]
        
    raw = _get(f"/senador/{cod_str}")
    if not raw:
        return None
        
    _cache_senadores[cod_str] = raw
    return raw