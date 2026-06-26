"""
Schemas Pydantic para os endpoints de gráficos.

Este arquivo deixa explícito o contrato JSON descrito na SPEC do Dashboard.
Assim, o FastAPI valida a resposta e a documentação automática fica alinhada
com o que o frontend espera consumir.
"""

from pydantic import BaseModel


class ItemDistribuicao(BaseModel):
    """Representa uma barra/fatia do gráfico retornado para o Dashboard."""

    label: str
    total: int


class IndicadoresDistribuicao(BaseModel):
    """Representa os três cards de indicadores definidos na SPEC."""

    total_pls: int
    partido_mais_ativo: str | None
    estado_mais_ativo: str | None


class DistribuicaoResponse(BaseModel):
    """Resposta completa do endpoint GET /api/graficos/distribuicao."""

    comparar_por: str
    data_atualizacao: str
    indicadores: IndicadoresDistribuicao
    dados: list[ItemDistribuicao]
