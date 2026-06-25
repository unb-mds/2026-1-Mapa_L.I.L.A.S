"""
app/services/camara_client.py

Cliente HTTP para a API da Câmara dos Deputados (v2).
Responsabilidade exclusiva: fazer requisições e retornar JSON bruto.
Não persiste, não normaliza, não conhece os modelos do banco.

Base URL: https://dadosabertos.camara.leg.br/api/v2
"""

import logging
from typing import Any, Iterator, Optional
import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://dadosabertos.camara.leg.br/api/v2"
TIMEOUT = 30
ITENS_POR_PAGINA = 100

PALAVRAS_CHAVE = [
    "feminicídio",
    "violência doméstica",
    "direitos da mulher",
]

SIGLAS_TIPO = ["PL", "PLP"]

_cache_deputados = {}

def _get(path: str, params: Optional[dict] = None) -> Optional[dict[str, Any]]:
    url = f"{BASE_URL}/{path.lstrip('/')}"
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as exc:
        logger.warning("Câmara API indisponível [%s]: %s", url, exc)
        return None

from datetime import date, timedelta

def listar_proposicoes(
    sigla_tipo: str,
    keyword: str,
    ano_inicial: Optional[int] = None,
    numdias: Optional[int] = None,
) -> Iterator[dict[str, Any]]:
    pagina = 1
    while True:
        # Parâmetros atualizados para a especificação v2 da Câmara
        params: dict[str, Any] = {
            "siglaTipo": sigla_tipo,
            "keywords": PALAVRAS_CHAVE,
            "itens": ITENS_POR_PAGINA,
            "pagina": pagina,
            "ordem": "ASC",
            "ordenarPor": "id",
        }
        if ano_inicial:
            params["dataApresentacaoInicio"] = f"{ano_inicial}-01-01"
        elif numdias is not None:
            data_inicio = (date.today() - timedelta(days=numdias)).isoformat()
            params["dataInicio"] = data_inicio

        raw = _get("/proposicoes", params)
        if not raw:
            break

        dados = raw.get("dados", [])
        if not dados:
            break

        yield from dados

        links = raw.get("links", [])
        tem_proxima = any(lnk.get("rel") == "next" for lnk in links)
        if not tem_proxima:
            break
        pagina += 1

def buscar_detalhe(id_proposicao: int) -> Optional[dict[str, Any]]:
    raw = _get(f"/proposicoes/{id_proposicao}")
    if not raw:
        return None
    return raw.get("dados")

def buscar_autores(id_proposicao: int) -> list[dict[str, Any]]:
    raw = _get(f"/proposicoes/{id_proposicao}/autores")
    if not raw:
        return []
    return raw.get("dados", [])

def buscar_tramitacoes(id_proposicao: int) -> list[dict[str, Any]]:
    raw = _get(f"/proposicoes/{id_proposicao}/tramitacoes")
    if not raw:
        return []
    return raw.get("dados", [])

def buscar_deputado(id_deputado: int) -> Optional[dict[str, Any]]:
    id_str = str(id_deputado)
    if id_str in _cache_deputados:
        return _cache_deputados[id_str]
        
    raw = _get(f"/deputados/{id_str}")
    if not raw:
        return None
        
    dados = raw.get("dados", {})
    _cache_deputados[id_str] = dados
    return dados