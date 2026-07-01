from pydantic import BaseModel, ConfigDict
from typing import Optional

class CamaraProposicaoSchema(BaseModel):
    id: int
    siglaTipo: str
    numero: int
    ano: int
    ementa: Optional[str] = None
    
    model_config = ConfigDict(extra='ignore')

class SenadoProposicaoSchema(BaseModel):
    # O collector do senado extrai campos básicos da materia
    # Para validar minimamente, exigiremos pelo menos um identificador único
    id: str | int
    identificacao: Optional[str] = None
    codigoMateria: Optional[str | int] = None
    
    model_config = ConfigDict(extra='ignore')
