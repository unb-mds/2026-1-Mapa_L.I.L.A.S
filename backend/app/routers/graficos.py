"""
Rotas de gráficos consumidas pelo frontend do Dashboard.

O prefixo segue exatamente a SPEC: /api/graficos.
"""

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.graficos import DistribuicaoResponse
from app.services.graficos import obter_distribuicao


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

    return obter_distribuicao(
        db=db,
        comparar_por=comparar_por,
        estado=estado,
        partido=partido,
        genero=genero,
        mes=mes,
    )
