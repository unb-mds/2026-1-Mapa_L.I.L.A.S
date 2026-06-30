"""
app/models.py

Modelos SQLAlchemy para o Mapa L.I.L.A.S.

Tabelas implementadas conforme spec (CLAUDE_MapaLILAS.md) com adições
necessárias para os critérios de aceitação:
  - dados_raw JSONB em pls_senado e pls_camara (ADR-002)
  - tramitacao_senado e tramitacao_camara (RF05: histórico por proposição)
  - updated_at em todas as tabelas mutáveis (rastreabilidade)

Nota arquitetural: autoria_camara e autoria_senado são tabelas separadas
conforme spec. Queries cross-house (ex: "todos os autores de PLs sobre
feminicídio") requerem UNION. Caso isso vire gargalo, consolide em uma
tabela autoria(casa, id_pl, id_parlamentar).
"""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.types import JSON

JSONB = PG_JSONB().with_variant(JSON, "sqlite")


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Proposições — Senado Federal
# ---------------------------------------------------------------------------

class PlSenado(Base):
    __tablename__ = "pls_senado"

    id = Column(Integer, primary_key=True, nullable=False)
    codigo_materia = Column(Integer, nullable=False)
    identificacao = Column(String, nullable=False)
    data_apresentacao = Column(Date, nullable=True)
    data_deliberacao = Column(Date, nullable=True)
    ementa = Column(Text, nullable=False)
    objetivo = Column(String, nullable=True)
    tipo_documento = Column(String, nullable=True)
    tramitando = Column(Boolean, nullable=True)
    sigla_tipo_deliberacao = Column(String, nullable=True)
    dados_raw = Column(JSONB, nullable=True)                          # ADR-002
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(
    ), onupdate=func.now(), nullable=False)

    autorias = relationship(
        "AutoriaSenado", back_populates="pl", cascade="all, delete-orphan")
    tramitacoes = relationship("TramitacaoSenado", back_populates="pl", cascade="all, delete-orphan",
                               order_by="TramitacaoSenado.sequencia")


# ---------------------------------------------------------------------------
# Proposições — Câmara dos Deputados
# ---------------------------------------------------------------------------

class PlCamara(Base):
    __tablename__ = "pls_camara"

    id = Column(Integer, primary_key=True, nullable=False)
    numero = Column(Integer, nullable=False)
    ano = Column(Integer, nullable=True)
    sigla_tipo = Column(String, nullable=True)
    uri = Column(String, nullable=True)
    data_apresentacao = Column(DateTime(timezone=True), nullable=True)
    ementa = Column(Text, nullable=False)
    descricao_tipo = Column(String, nullable=True)
    descricao_situacao = Column(String, nullable=True)
    despacho = Column(Text, nullable=True)
    dados_raw = Column(JSONB, nullable=True)                          # ADR-002
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(
    ), onupdate=func.now(), nullable=False)

    autorias = relationship(
        "AutoriaCamara", back_populates="pl", cascade="all, delete-orphan")
    tramitacoes = relationship("TramitacaoCamara", back_populates="pl", cascade="all, delete-orphan",
                               order_by="TramitacaoCamara.sequencia")


# ---------------------------------------------------------------------------
# Parlamentares (Câmara + Senado unificados)
# ---------------------------------------------------------------------------

class Parlamentar(Base):
    __tablename__ = "parlamentares"
    __table_args__ = (
        CheckConstraint("casa IN ('Câmara', 'Senado')",
                        name="ck_parlamentares_casa"),
        CheckConstraint("sexo IN ('F', 'M')", name="ck_parlamentares_sexo"),
    )

    # "cam_141492" ou "sen_5783"
    id = Column(String, primary_key=True, nullable=False)
    casa = Column(String, nullable=False)
    nome_eleitoral = Column(String, nullable=False)
    nome_civil = Column(String, nullable=True)
    sigla_partido = Column(String, nullable=False)
    sigla_uf = Column(String(2), nullable=True)
    # "F" ou "M"
    sexo = Column(String(1), nullable=False)
    url_foto = Column(String, nullable=True)
    status_mandato = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(
    ), onupdate=func.now(), nullable=False)

    autorias_camara = relationship(
        "AutoriaCamara", back_populates="parlamentar")
    autorias_senado = relationship(
        "AutoriaSenado", back_populates="parlamentar")


# ---------------------------------------------------------------------------
# Autorias — separadas por casa conforme spec
# ---------------------------------------------------------------------------

class AutoriaCamara(Base):
    __tablename__ = "autoria_camara"

    id_pl = Column(Integer, ForeignKey("pls_camara.id",
                   ondelete="CASCADE"), primary_key=True, nullable=False)
    id_parlamentar = Column(String, ForeignKey(
        "parlamentares.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    tipo_autoria = Column(String, nullable=True)

    pl = relationship("PlCamara", back_populates="autorias")
    parlamentar = relationship("Parlamentar", back_populates="autorias_camara")


class AutoriaSenado(Base):
    __tablename__ = "autoria_senado"

    id_pl = Column(Integer, ForeignKey("pls_senado.id",
                   ondelete="CASCADE"), primary_key=True, nullable=False)
    id_parlamentar = Column(String, ForeignKey(
        "parlamentares.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    tipo_autoria = Column(String, nullable=True)

    pl = relationship("PlSenado", back_populates="autorias")
    parlamentar = relationship("Parlamentar", back_populates="autorias_senado")


# ---------------------------------------------------------------------------
# Tramitações — RF05: rota /proposicao/{id} exige histórico completo
# ---------------------------------------------------------------------------

class TramitacaoSenado(Base):
    __tablename__ = "tramitacao_senado"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_pl = Column(Integer, ForeignKey("pls_senado.id",
                   ondelete="CASCADE"), nullable=False)
    data_tramitacao = Column(Date, nullable=True)
    situacao = Column(String, nullable=True)
    descricao = Column(Text, nullable=True)
    local = Column(String, nullable=True)
    sequencia = Column(Integer, nullable=True)
    dados_raw = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)

    pl = relationship("PlSenado", back_populates="tramitacoes")


class TramitacaoCamara(Base):
    __tablename__ = "tramitacao_camara"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_pl = Column(Integer, ForeignKey("pls_camara.id",
                   ondelete="CASCADE"), nullable=False)
    data_tramitacao = Column(DateTime(timezone=True), nullable=True)
    situacao = Column(String, nullable=True)
    descricao = Column(Text, nullable=True)
    local = Column(String, nullable=True)
    sequencia = Column(Integer, nullable=True)
    dados_raw = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now(), nullable=False)

    pl = relationship("PlCamara", back_populates="tramitacoes")
