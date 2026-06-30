from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, cast, String, Integer, null, case
from app.database import get_db
from app.models import (
    PlCamara, PlSenado, Parlamentar, AutoriaCamara, AutoriaSenado,
    TramitacaoCamara, TramitacaoSenado
)
import math
import re  # <-- IMPORTANTE: Adicionado para usar regex na rota de filtros

def mapear_estagio_atual_senado(situacao: str) -> str:
    if not situacao:
        return "rejeitado"
    situacao = situacao.upper()
    if situacao in ["AGDESP"]:
        return "apresentacao"
    if situacao in ["AGDREL", "RELATOR", "PRONTPAUT"]:
        return "comissao"
    if situacao in ["INPAUTA", "RMCD"]:
        return "votacao"
    if situacao in ["RMSAN"]:
        return "sancao"
    if situacao in ["TNJR", "TNJRVETO"]:
        return "transformado em normajuridica"
    if situacao in ["RJTDA", "PRJDA", "RTPA", "ARQVD", "ARQV_CD"]:
        return "rejeitado"
    return "apresentacao"  # Fallback

def mapear_estagio_atual_camara(situacao: str) -> str:
    if not situacao:
        return "rejeitado"
    if situacao in [
        "Aguardando Recebimento",
        "Aguardando Despacho do Presidente da Câmara dos Deputados",
        "Aguardando Despacho do Presidente da Câmara dos Deputados (Análise)",
        "Aguardando Despacho do Presidente da Câmara dos Deputados (Autorização)",
        "Aguardando Despacho do Presidente da Câmara dos Deputados (Chancela)",
        "Aguardando Chancela e Publicação do Despacho",
        "Aguardando Autorização do Despacho",
        "Aguardando Encaminhamento"
    ]:
        return "apresentacao"
    if situacao in [
        "Aguardando Designação de Relator(a)",
        "Aguardando Designação - Aguardando Devolução de Relator(a) que deixou de ser Membro",
        "Aguardando Parecer",
        "Ag. Análise de Inconstitucionalidade",
        "Aguardando Vistas",
        "Tramitando em Conjunto"
    ]:
        return "comissao"
    if situacao in [
        "Pronta para Pauta",
        "Aguardando Deliberação de Recurso"
    ]:
        return "votacao"
    if situacao in [
        "Transformado em Norma Jurídica",
        "Vetado totalmente",
        "Aguardando Apreciação do Veto"
    ]:
        return "sancao"
    if situacao in [
        "Arquivada",
        "Devolvida ao(à) Autor(a)",
        "Retirado pelo(a) Autor(a)"
    ]:
        return "rejeitado"
    return "apresentacao"  # Fallback

def extrair_temas(temas_raw: str) -> list:
    if not temas_raw:
        return []
    # Replace the dot at the end for Senate
    temas_raw = temas_raw.rstrip(".")
    # Split by comma and strip whitespaces
    return [t.strip() for t in temas_raw.split(",") if t.strip()]

router = APIRouter(prefix="/api/projetos-de-lei")

@router.get("")
def listar_projetos(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    keyword: str = None,
    partido: str = None,
    uf: str = None,
    status: str = None,
    ano: int = None,
    ordenar: str = Query("recentes")
):
    # 1. Subqueries para a última atualização
    subq_camara = (
        select(TramitacaoCamara.id_pl, func.max(TramitacaoCamara.data_tramitacao).label("ultima_atualizacao"))
        .group_by(TramitacaoCamara.id_pl)
        .subquery()
    )
    
    subq_senado = (
        select(TramitacaoSenado.id_pl, func.max(TramitacaoSenado.data_tramitacao).label("ultima_atualizacao"))
        .group_by(TramitacaoSenado.id_pl)
        .subquery()
    )

    # 1.1 Subqueries para unificar autores
    subq_autor_camara = (
        select(
            AutoriaCamara.id_pl,
            func.min(Parlamentar.nome_eleitoral).label("autor_nome"),
            func.min(Parlamentar.sigla_partido).label("autor_partido"),
            func.min(Parlamentar.sigla_uf).label("autor_uf")
        )
        .join(Parlamentar, Parlamentar.id == AutoriaCamara.id_parlamentar)
        .group_by(AutoriaCamara.id_pl)
        .subquery()
    )

    subq_autor_senado = (
        select(
            AutoriaSenado.id_pl,
            func.min(Parlamentar.nome_eleitoral).label("autor_nome"),
            func.min(Parlamentar.sigla_partido).label("autor_partido"),
            func.min(Parlamentar.sigla_uf).label("autor_uf")
        )
        .join(Parlamentar, Parlamentar.id == AutoriaSenado.id_parlamentar)
        .group_by(AutoriaSenado.id_pl)
        .subquery()
    )

    # 2. Query Base da Câmara
    status_camara = case(
        (PlCamara.descricao_situacao == "Transformado em Norma Jurídica", "aprovado"),
        (PlCamara.descricao_situacao == "Arquivada", "arquivado"),
        else_="em_tramitacao"
    ).label("status_normalizado")

    query_camara = (
        select(
            func.cast(PlCamara.id, String).label("raw_id"),
            func.cast(PlCamara.numero, String).label("numero"),
            func.cast(PlCamara.ano, String).label("ano"), 
            func.cast("CÂMARA DOS DEPUTADOS", String).label("casa"),
            func.cast(PlCamara.descricao_situacao, String).label("raw_status"),
            PlCamara.ementa.label("ementa"),
            subq_autor_camara.c.autor_nome,
            subq_autor_camara.c.autor_partido,
            subq_autor_camara.c.autor_uf,
            func.coalesce(subq_camara.c.ultima_atualizacao, PlCamara.updated_at).label("ultima_atualizacao"),
            status_camara
        )
        .outerjoin(subq_camara, subq_camara.c.id_pl == PlCamara.id)
        .outerjoin(subq_autor_camara, subq_autor_camara.c.id_pl == PlCamara.id)
    )

    # 3. Query Base do Senado (EXTRAÇÃO ROBUSTA COM REGEX)
    # Extrai o grupo de dígitos imediatamente antes da barra: ex "PL 1029/2026 (Sub)" -> "1029"
    numero_senado = func.substring(PlSenado.identificacao, '([0-9]+)/')
    
    # Extrai exatamente 4 dígitos imediatamente após a barra: ex "PL 1029/2026 (Sub)" -> "2026"
    ano_senado = func.substring(PlSenado.identificacao, '/([0-9]{4})')

    situacao_atual_senado = func.upper(func.cast(PlSenado.dados_raw['situacaoAtual'].astext, String))

    status_senado = case(
        (situacao_atual_senado.in_(["TNJR", "TNJRVETO"]), "aprovado"),
        (or_(situacao_atual_senado.in_(["ARQVD", "ARQV_CD", "PRJDA", "RJTDA", "RTPA"]), situacao_atual_senado.is_(None), situacao_atual_senado == 'NULL', situacao_atual_senado == ''), "arquivado"),
        else_="em_tramitacao"
    ).label("status_normalizado")

    query_senado = (
        select(
            func.cast(PlSenado.id, String).label("raw_id"),
            func.cast(func.nullif(numero_senado, ''), String).label("numero"),
            func.cast(func.nullif(ano_senado, ''), String).label("ano"), 
            func.cast("SENADO FEDERAL", String).label("casa"),
            func.cast(null(), String).label("raw_status"), 
            PlSenado.ementa.label("ementa"),
            subq_autor_senado.c.autor_nome,
            subq_autor_senado.c.autor_partido,
            subq_autor_senado.c.autor_uf,
            func.coalesce(subq_senado.c.ultima_atualizacao, PlSenado.updated_at).label("ultima_atualizacao"),
            status_senado
        )
        .outerjoin(subq_senado, subq_senado.c.id_pl == PlSenado.id)
        .outerjoin(subq_autor_senado, subq_autor_senado.c.id_pl == PlSenado.id)
    )

    # 4. UNION ALL e Deduplicação
    union_subq = query_camara.union_all(query_senado).subquery()
    
    rn_col = func.row_number().over(
        partition_by=(union_subq.c.numero, union_subq.c.ano),
        order_by=union_subq.c.ultima_atualizacao.desc().nullslast()
    ).label('rn')
    
    dedup_subq = select(union_subq, rn_col).subquery()
    
    final_query = select(dedup_subq).where(dedup_subq.c.rn == 1)

    # 5. Aplicação de Filtros
    if keyword:
        termo = f"%{keyword}%"
        final_query = final_query.where(
            or_(
                dedup_subq.c.ementa.ilike(termo),
                dedup_subq.c.numero.ilike(termo)
            )
        )
    if partido:
        final_query = final_query.where(dedup_subq.c.autor_partido == partido)
    if uf:
        final_query = final_query.where(dedup_subq.c.autor_uf == uf)
    if ano:
        final_query = final_query.where(dedup_subq.c.ano == str(ano))
    if status:
        final_query = final_query.where(dedup_subq.c.status_normalizado == status)

    # 6. Ordenação
    if ordenar == "recentes":
        final_query = final_query.order_by(dedup_subq.c.ultima_atualizacao.desc())
    elif ordenar == "antigos":
        final_query = final_query.order_by(dedup_subq.c.ultima_atualizacao.asc())
    elif ordenar == "numero_asc":
        # Continua usando regex para garantir a conversão limpa em Inteiro na ordenação
        numero_limpo = func.regexp_replace(dedup_subq.c.numero, '[^0-9]', '', 'g')
        final_query = final_query.order_by(cast(func.nullif(numero_limpo, ''), Integer).asc())

    # 7. Execução e Paginação
    total_items = db.execute(select(func.count()).select_from(final_query.subquery())).scalar()
    
    offset = (page - 1) * per_page
    final_query = final_query.offset(offset).limit(per_page)
    
    resultados = db.execute(final_query).fetchall()

    # 8. Montagem do Payload de Resposta
    projetos = []
    for row in resultados:
        projetos.append({
            "id": f"pl-{row.numero}-{row.ano}",
            "numero": str(row.numero) if row.numero else None,
            "ano": int(row.ano) if row.ano and str(row.ano).isdigit() else None, 
            "casa": row.casa,
            "status": row.status_normalizado,
            "autor_nome": row.autor_nome,
            "autor_partido": row.autor_partido,
            "autor_uf": row.autor_uf,
            "ementa": row.ementa,
            "ultima_atualizacao": row.ultima_atualizacao.strftime("%Y-%m-%d") if row.ultima_atualizacao else None
        })

    return {"projetos": projetos, "total": total_items, "page": page, "per_page": per_page, "total_pages": math.ceil(total_items / per_page) if per_page else 1}

@router.get("/{casa}/{numero}/{ano}")
def obter_projeto_detalhado(casa: str, numero: str, ano: int, db: Session = Depends(get_db)):
    casa_low = casa.lower()
    
    if casa_low in ["camara", "câmara", "camara dos deputados", "câmara dos deputados"]:
        pl = db.query(PlCamara).filter(
            PlCamara.numero == int(numero), 
            PlCamara.ano == ano
        ).order_by(PlCamara.updated_at.desc()).first()
        
        if not pl:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
            
        dados_raw = pl.dados_raw or {}
        
        autores_nomes = []
        autores_partidos = []
        autores_ufs = []
        for autoria in pl.autorias:
            if autoria.parlamentar:
                autores_nomes.append(autoria.parlamentar.nome_eleitoral)
                if autoria.parlamentar.sigla_partido:
                    autores_partidos.append(autoria.parlamentar.sigla_partido)
                if autoria.parlamentar.sigla_uf:
                    autores_ufs.append(autoria.parlamentar.sigla_uf)
                    
        historico = []
        for t in pl.tramitacoes:
            historico.append({
                "data": t.data_tramitacao.strftime("%d/%m/%Y") if t.data_tramitacao else None,
                "titulo": t.situacao or "Tramitação",
                "descricao": t.descricao
            })
        historico.reverse()
        
        if pl.descricao_situacao == "Transformado em Norma Jurídica":
            status_camara = "aprovado"
        elif pl.descricao_situacao == "Arquivada":
            status_camara = "arquivado"
        else:
            status_camara = "em_tramitacao"

        # O contrato atualizado especificou "Câmara dos Deputados"
        return {
            "numero": str(pl.numero),
            "ano": pl.ano,
            "casa": "Câmara dos Deputados",
            "status": status_camara,
            "regime": None,
            "data_apresentacao": pl.data_apresentacao.strftime("%d/%m/%Y") if pl.data_apresentacao else None,
            "autor_nome": autores_nomes[0] if autores_nomes else None,
            "autor_partido": autores_partidos[0] if autores_partidos else None,
            "autor_uf": autores_ufs[0] if autores_ufs else None,
            "ementa": pl.ementa,
            "estagio_atual": "aprovado" if status_camara == "aprovado" else mapear_estagio_atual_camara(pl.descricao_situacao),
            "url_pdf": dados_raw.get("urlInteiroTeor"),
            "temas": extrair_temas(dados_raw.get("keywords")),
            "historico": historico
        }
        
    elif casa_low in ["senado", "senado federal"]:
        pl = db.query(PlSenado).filter(
            PlSenado.identificacao.ilike(f"%{numero}/{ano}%")
        ).order_by(PlSenado.updated_at.desc()).first()
        
        if not pl:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")
            
        dados_raw = pl.dados_raw or {}
        
        autores_nomes = []
        autores_partidos = []
        autores_ufs = []
        for autoria in pl.autorias:
            if autoria.parlamentar:
                autores_nomes.append(autoria.parlamentar.nome_eleitoral)
                if autoria.parlamentar.sigla_partido:
                    autores_partidos.append(autoria.parlamentar.sigla_partido)
                if autoria.parlamentar.sigla_uf:
                    autores_ufs.append(autoria.parlamentar.sigla_uf)
                    
        historico = []
        for t in pl.tramitacoes:
            historico.append({
                "data": t.data_tramitacao.strftime("%d/%m/%Y") if t.data_tramitacao else None,
                "titulo": t.situacao or "Tramitação",
                "descricao": t.descricao
            })
        historico.reverse()
        
        situacao_atual = dados_raw.get("situacaoAtual")
        status_raw = situacao_atual.upper() if situacao_atual else None
        
        if status_raw in ["TNJR", "TNJRVETO"]:
            status_senado = "aprovado"
        elif not status_raw or status_raw in ["ARQVD", "ARQV_CD", "PRJDA", "RJTDA", "RTPA"]:
            status_senado = "arquivado"
        else:
            status_senado = "em_tramitacao"

        return {
            "numero": str(numero),
            "ano": ano,
            "casa": "Senado Federal",
            "status": status_senado,
            "regime": None,
            "data_apresentacao": pl.data_apresentacao.strftime("%d/%m/%Y") if pl.data_apresentacao else None,
            "autor_nome": autores_nomes[0] if autores_nomes else None,
            "autor_partido": autores_partidos[0] if autores_partidos else None,
            "autor_uf": autores_ufs[0] if autores_ufs else None,
            "ementa": pl.ementa,
            "estagio_atual": mapear_estagio_atual_senado(dados_raw.get("situacaoAtual")),
            "url_pdf": dados_raw.get("documento", {}).get("url") if isinstance(dados_raw.get("documento"), dict) else None,
            "temas": extrair_temas(dados_raw.get("documento", {}).get("indexacao") if isinstance(dados_raw.get("documento"), dict) else None),
            "historico": historico
        }
    else:
        raise HTTPException(status_code=400, detail="Casa legislativa inválida. Use 'camara' ou 'senado'.")

@router.get("/filtros")
def listar_filtros(db: Session = Depends(get_db)):
    partidos_query = db.query(Parlamentar.sigla_partido).filter(
        Parlamentar.sigla_partido.isnot(None), 
        Parlamentar.sigla_partido != ""
    ).distinct().order_by(Parlamentar.sigla_partido).all()
    
    ufs_query = db.query(Parlamentar.sigla_uf).filter(
        Parlamentar.sigla_uf.isnot(None), 
        Parlamentar.sigla_uf != ""
    ).distinct().order_by(Parlamentar.sigla_uf).all()
    
    anos_camara = db.query(PlCamara.ano).filter(PlCamara.ano.isnot(None)).distinct().all()
    anos_set = {ano[0] for ano in anos_camara}
    
    identificacoes_senado = db.query(PlSenado.identificacao).filter(PlSenado.identificacao.isnot(None)).all()
    
    for id_senado in identificacoes_senado:
        texto = id_senado[0] 
        if texto and "/" in texto:
            # EXTRAÇÃO ROBUSTA COM REGEX NO PYTHON
            # Busca exatamente a barra seguida de 4 dígitos, ignorando o resto
            match = re.search(r'/([0-9]{4})', texto)
            if match:
                anos_set.add(int(match.group(1)))
                
    anos_lista = sorted(list(anos_set))
    
    return {
        "partidos": [p[0] for p in partidos_query],
        "ufs": [u[0] for u in ufs_query],
        "anos": anos_lista
    }