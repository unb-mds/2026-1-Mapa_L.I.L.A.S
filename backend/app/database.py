"""
backend/database.py

Configuração do engine SQLAlchemy e criação das tabelas.

Uso direto (criar tabelas):
    python -m backend.database

Uso no FastAPI (importar session):
    from backend.database import get_session
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.models import Base

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:suasenha@db:5432/mapa_lilas",
)

# NullPool: correto para ambientes serverless (Vercel).
# Cada requisição abre/fecha sua própria conexão; o pooling real fica no pgbouncer do Neon.
engine = create_engine(DATABASE_URL, echo=False, poolclass=NullPool)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session():
    """Dependency do FastAPI — uso: Depends(get_session)."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def create_tables() -> None:
    """Cria todas as tabelas definidas nos models. Idempotente: ignora tabelas que já existem."""
    print(f"[INFO] Conectando em: {DATABASE_URL.split('@')[-1]}")
    Base.metadata.create_all(bind=engine)
    print("[INFO] Tabelas criadas (ou já existentes):")
    with engine.connect() as conn:
        result = conn.execute(text(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
        ))
        for row in result:
            print(f"  ✓ {row[0]}")


if __name__ == "__main__":
    create_tables()


def get_db():
    """
    Gera uma sessão do banco de dados para cada requisição 
    e a fecha automaticamente ao final.
    """
    db = SessionLocal() # ATENÇÃO: se o seu sessionmaker tiver outro nome, altere aqui.
    try:
        yield db
    finally:
        db.close()
