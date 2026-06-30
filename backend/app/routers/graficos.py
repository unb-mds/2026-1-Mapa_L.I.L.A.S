"""
Rotas de gráficos consumidas pelo frontend do Dashboard.

O prefixo segue exatamente a SPEC: /api/graficos.
"""

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.graficos import DistribuicaoResponse, ResumoResponse
from app.services.graficos import obter_distribuicao, obter_resumo
from app.cache import cache_resumo, cache_distribuicao


# Router separado para manter responsabilidades de gráficos fora de projeto.py.
router = APIRouter(prefix="/api/graficos")


@router.get("/distribuicao", response_model=DistribuicaoResponse)
def distribuicao(
    db: Session = Depends(get_db),
    comparar_por: Literal["partido", "estado", "genero", "mes"] = Query(...),
    estado: str | None = Query(None),
    partido: str | None = Query(None),
    genero: Literal["masculino", "feminino"] | None = Query(None),
    mes: int | None = Query(None, ge=1, le=12),
):
    """
    Retorna a distribuição de PLs para o Dashboard Detalhado.

    A camada de serviço aplica a regra da SPEC que ignora o filtro igual à
    dimensão ativa, por exemplo: comparar_por=estado ignora o parâmetro estado.
    """

    cache_key = f"{comparar_por}_{estado}_{partido}_{genero}_{mes}"
    if cache_key in cache_distribuicao:
        return cache_distribuicao[cache_key]
        
    resultado = obter_distribuicao(
        db=db,
        comparar_por=comparar_por,
        estado=estado,
        partido=partido,
        genero=genero,
        mes=mes,
    )
    cache_distribuicao[cache_key] = resultado
    return resultado


@router.get("/resumo", response_model=ResumoResponse)
def resumo(db: Session = Depends(get_db)):
    """
    Retorna os indicadores resumidos para a página Mapa L.I.L.A.S. (Gráficos),
    como tempo médio de tramitação, ranking de estados e parlamentares ativos.
    """
    if "resumo" in cache_resumo:
        return cache_resumo["resumo"]
        
    resultado = obter_resumo(db)
    cache_resumo["resumo"] = resultado
    return resultado
