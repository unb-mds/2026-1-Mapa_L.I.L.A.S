"""
Schemas Pydantic para os endpoints de projetos de lei e filtros.
Isso sela o contrato da API com o frontend.
"""
from pydantic import BaseModel
from typing import Optional, List

class ProjetoItem(BaseModel):
    id: str
    numero: Optional[str] = None
    ano: Optional[int] = None
    casa: str
    status: str
    autor_nome: Optional[str] = None
    autor_partido: Optional[str] = None
    autor_uf: Optional[str] = None
    ementa: Optional[str] = None
    ultima_atualizacao: Optional[str] = None

class ProjetosResponse(BaseModel):
    projetos: List[ProjetoItem]
    total: int
    page: int
    per_page: int
    total_pages: int

class StatsResponse(BaseModel):
    total: int
    em_tramitacao: int
    aprovados: int
    arquivados: int

class FiltrosResponse(BaseModel):
    partidos: List[str]
    ufs: List[str]
    anos: List[int]
