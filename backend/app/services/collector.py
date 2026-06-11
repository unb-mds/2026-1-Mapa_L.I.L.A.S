"""
app/services/collector.py

Orquestrador de coleta: coordena clientes HTTP → schemas → normalizer → banco.
"""

import asyncio
import logging
from datetime import date
from typing import Optional
import time
from sqlalchemy.orm import Session

from app import services  
from app.services import camara_client, senado_client
from app.services.normalizer import (
    upsert_autores_camara,
    upsert_autores_senado,
    upsert_pl_camara,
    upsert_pl_senado,
    upsert_tramitacoes_camara,
    upsert_tramitacoes_senado,
)

logger = logging.getLogger(__name__)

INTERVALO_HORAS = 2

# ---------------------------------------------------------------------------
# Câmara
# ---------------------------------------------------------------------------

def coletar_camara(session: Session, ano_inicial: Optional[int] = None, numdias: Optional[int] = None) -> int:
    total = 0
    for sigla in camara_client.SIGLAS_TIPO:
        for kw in camara_client.PALAVRAS_CHAVE:
            logger.info("Câmara — coletando %s | keyword='%s'", sigla, kw)
            for item_raw in camara_client.listar_proposicoes(sigla, kw, ano_inicial, numdias):
                pl_id = item_raw.get("id")
                if not pl_id:
                    continue

                # 1. Busca os autores PRIMEIRO para verificar a origem do PL
                autores_raw = camara_client.buscar_autores(pl_id)
                
                # 2. Verifica se algum autor possui a tag do Senado
                ignorar_pl = False
                for autor in autores_raw:
                    nome_autor = autor.get("nome", "")
                    if "Senado Federal -" in nome_autor:
                        ignorar_pl = True
                        break
                
                # 3. Se for do Senado, ignora completamente a inserção na tabela da Câmara
                if ignorar_pl:
                    logger.info("Câmara — ignorando PL %s (Origem: Senado)", pl_id)
                    continue

                # 4. Se passou pelo filtro, segue a coleta normal
                detalhe_raw = camara_client.buscar_detalhe(pl_id)
                id_salvo = upsert_pl_camara(session, item_raw, detalhe_raw, item_raw)
                if not id_salvo:
                    continue

                # ENRIQUECIMENTO DE CACHE: Deputados
                for autor in autores_raw:
                    uri = autor.get("uri")
                    if uri and "/deputados/" in uri:
                        dep_id = uri.rstrip("/").split("/")[-1]
                        detalhes = camara_client.buscar_deputado(dep_id)
                        if detalhes:
                            autor["detalhes_deputado"] = detalhes
                            
                upsert_autores_camara(session, id_salvo, autores_raw)

                tramitacoes_raw = camara_client.buscar_tramitacoes(pl_id)
                upsert_tramitacoes_camara(session, id_salvo, tramitacoes_raw)

                session.commit()
                total += 1

    logger.info("Câmara — ciclo concluído. %d registros processados.", total)
    return total

# ---------------------------------------------------------------------------
# Senado
# ---------------------------------------------------------------------------

def coletar_senado(
    session: Session,
    ano_inicial: Optional[int] = None,
    numdias: Optional[int] = None,
) -> int:
    total = 0
    for sigla in senado_client.SIGLAS_TIPO:
        for kw in senado_client.PALAVRAS_CHAVE:
            logger.info("Senado — coletando %s | keyword='%s'", sigla, kw)
            
            materias_raw = senado_client.pesquisar_materias(
                keyword=kw,
                sigla_tipo=sigla,
                ano_inicial=ano_inicial,
                numdias=numdias,
            )

            for item_raw in (materias_raw or []):
                
                # 1. Filtro Anti-Duplicação: Verifica se o PL veio da Câmara
                autoria_pl = item_raw.get("autoria", "")
                if "Câmara dos Deputados" in autoria_pl:
                    logger.info("Senado — ignorando %s (Origem: Câmara)", item_raw.get("identificacao"))
                    continue

                # 2. Se passou pelo filtro, segue a coleta normal
                id_salvo = upsert_pl_senado(session, item_raw, item_raw)
                if not id_salvo:
                    continue

                detalhe_raw = senado_client.buscar_detalhe(id_salvo)
                
                if detalhe_raw:
                    upsert_autores_senado(session, id_salvo, detalhe_raw)
                    upsert_tramitacoes_senado(session, id_salvo, detalhe_raw)

                session.commit()
                total += 1

    logger.info("Senado — ciclo concluído. %d registros processados.", total)
    return total
# ---------------------------------------------------------------------------
# Coleta incremental e Agendador
# ---------------------------------------------------------------------------
# DESATIVADO — ingestão movida para GitHub Actions (data-ingestion.yml)

# def executar_ciclo_incremental(session: Session) -> None:
#     logger.info("Iniciando ciclo incremental — %s", date.today())
#     try:
#         coletar_camara(session)
#     except Exception as exc:
#         logger.warning("Falha no ciclo incremental da Câmara: %s", exc)
#     try:
#         coletar_senado(session, numdias=1)
#     except Exception as exc:
#         logger.warning("Falha no ciclo incremental do Senado: %s", exc)
# 
# async def loop_coleta(get_session_func) -> None:
#     while True:
#         await asyncio.sleep(INTERVALO_HORAS * 3600)
#         logger.info("Agendador: disparando ciclo incremental.")
#         try:
#             await asyncio.to_thread(_ciclo_incremental_thread, get_session_func)
#         except Exception as exc:
#             logger.warning("Agendador: ciclo incremental falhou: %s", exc)
# 
# def _ciclo_incremental_thread(get_session_func) -> None:
#     session: Session = next(get_session_func())
#     try:
#         executar_ciclo_incremental(session)
#     finally:
#         session.close()