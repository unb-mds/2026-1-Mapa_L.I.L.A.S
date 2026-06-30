"""
Serviços de agregação para os gráficos do Dashboard.

A regra principal aqui é consultar somente o banco de dados local já populado
pelo processo de ingestão. Não há mock nem chamada externa nesta camada.
"""

from datetime import date, datetime

from sqlalchemy import Integer, String, cast, func, literal, select
from sqlalchemy.orm import Session

from app.models import AutoriaCamara, AutoriaSenado, Parlamentar, PlCamara, PlSenado


# Valores aceitos pela SPEC para a dimensão principal do gráfico.
COMPARACOES_ACEITAS = {"partido", "estado", "genero", "mes"}

# Conversão usada quando comparar_por=mes.
MESES_ABREVIADOS = {
    1: "Jan",
    2: "Fev",
    3: "Mar",
    4: "Abr",
    5: "Mai",
    6: "Jun",
    7: "Jul",
    8: "Ago",
    9: "Set",
    10: "Out",
    11: "Nov",
    12: "Dez",
}


def _formatar_data_br(data_raw: date | datetime | None) -> str:
    """Formata datas no padrão DD/MM/AAAA exigido pela SPEC."""

    if not data_raw:
        return ""
    return data_raw.strftime("%d/%m/%Y")


def _normalizar_genero(sexo: str | None) -> str | None:
    """Converte o sexo salvo no banco ('M'/'F') para o texto da resposta."""

    if sexo == "M":
        return "Masculino"
    if sexo == "F":
        return "Feminino"
    return None


def _base_proposicoes():
    """
    Monta uma base única com PLs da Câmara e do Senado.

    As duas casas têm tabelas de PL e autoria separadas, então usamos UNION ALL
    para obter uma estrutura comum para as agregações do Dashboard.
    """

    camara = (
        select(
            literal("camara").label("casa"),
            PlCamara.id.label("id_pl"),
            func.concat(literal("camara:"), cast(
                PlCamara.id, String)).label("proposicao_id"),
            PlCamara.data_apresentacao.label("data_apresentacao"),
            PlCamara.updated_at.label("data_atualizacao"),
            Parlamentar.sigla_partido.label("partido"),
            Parlamentar.sigla_uf.label("estado"),
            Parlamentar.sexo.label("sexo"),
        )
        .join(AutoriaCamara, AutoriaCamara.id_pl == PlCamara.id)
        .join(Parlamentar, Parlamentar.id == AutoriaCamara.id_parlamentar)
    )

    senado = (
        select(
            literal("senado").label("casa"),
            PlSenado.id.label("id_pl"),
            func.concat(literal("senado:"), cast(
                PlSenado.id, String)).label("proposicao_id"),
            PlSenado.data_apresentacao.label("data_apresentacao"),
            PlSenado.updated_at.label("data_atualizacao"),
            Parlamentar.sigla_partido.label("partido"),
            Parlamentar.sigla_uf.label("estado"),
            Parlamentar.sexo.label("sexo"),
        )
        .join(AutoriaSenado, AutoriaSenado.id_pl == PlSenado.id)
        .join(Parlamentar, Parlamentar.id == AutoriaSenado.id_parlamentar)
    )

    return camara.union_all(senado).subquery()


def _aplicar_filtros(query, base, comparar_por: str, filtros: dict):
    """
    Aplica os filtros da SPEC.

    Quando o filtro é igual à dimensão ativa, ele é ignorado. Exemplo:
    comparar_por=estado ignora o parâmetro estado.
    """

    estado = filtros.get("estado")
    partido = filtros.get("partido")
    genero = filtros.get("genero")
    mes = filtros.get("mes")

    if estado and comparar_por != "estado":
        query = query.where(func.upper(base.c.estado) == estado.upper())

    if partido and comparar_por != "partido":
        query = query.where(func.upper(base.c.partido) == partido.upper())

    if genero and comparar_por != "genero":
        sexo = {"masculino": "M", "feminino": "F"}.get(genero.lower())
        if sexo:
            query = query.where(base.c.sexo == sexo)

    if mes and comparar_por != "mes":
        query = query.where(
            cast(func.extract("month", base.c.data_apresentacao), Integer) == mes)

    return query


def _coluna_agrupamento(base, comparar_por: str):
    """Retorna a expressão SQL usada como label do agrupamento principal."""

    if comparar_por == "partido":
        return func.upper(base.c.partido)
    if comparar_por == "estado":
        return func.upper(base.c.estado)
    if comparar_por == "genero":
        return base.c.sexo
    return cast(func.extract("month", base.c.data_apresentacao), Integer)


def _aplicar_label_preenchido(query, label_col, comparar_por: str):
    """Remove grupos vazios sem comparar números com texto no caso de mês."""

    query = query.where(label_col.isnot(None))
    if comparar_por in {"partido", "estado"}:
        query = query.where(label_col != "")
    if comparar_por == "genero":
        query = query.where(label_col.in_(["M", "F"]))
    return query


def _label_resposta(comparar_por: str, label_raw) -> str | None:
    """Converte o valor agrupado do banco para o label previsto na SPEC."""

    if label_raw is None:
        return None
    if comparar_por == "genero":
        return _normalizar_genero(label_raw)
    if comparar_por == "mes":
        return MESES_ABREVIADOS.get(int(label_raw))
    return str(label_raw)


def _agregar_por_dimensao(db: Session, base, comparar_por: str, filtros: dict):
    """Agrupa os PLs pela dimensão solicitada e ordena por total decrescente."""

    label_col = _coluna_agrupamento(base, comparar_por).label("label")

    query = select(label_col, func.count(func.distinct(
        base.c.proposicao_id)).label("total")).select_from(base)
    query = _aplicar_filtros(query, base, comparar_por, filtros)
    query = _aplicar_label_preenchido(query, label_col, comparar_por)
    query = query.group_by(label_col).order_by(
        func.count(func.distinct(base.c.proposicao_id)).desc())

    dados = []
    for row in db.execute(query).all():
        label = _label_resposta(comparar_por, row.label)
        if label:
            dados.append({"label": label, "total": row.total})
    return dados


def _total_pls(db: Session, base, comparar_por: str, filtros: dict) -> int:
    """Calcula o total de registros considerados após os filtros válidos."""

    query = select(func.count(func.distinct(
        base.c.proposicao_id))).select_from(base)
    query = _aplicar_filtros(query, base, comparar_por, filtros)
    return db.execute(query).scalar() or 0


def _mais_ativo(db: Session, base, comparar_por: str, filtros: dict, campo: str) -> str | None:
    """Calcula o partido ou estado com mais propostas após os filtros."""

    label_col = func.upper(getattr(base.c, campo)).label("label")
    query = select(label_col, func.count(func.distinct(
        base.c.proposicao_id)).label("total")).select_from(base)
    query = _aplicar_filtros(query, base, comparar_por, filtros)
    query = query.where(label_col.isnot(None), label_col != "")
    query = query.group_by(label_col).order_by(func.count(
        func.distinct(base.c.proposicao_id)).desc()).limit(1)

    row = db.execute(query).first()
    return row.label if row else None


def _data_atualizacao(db: Session, base, comparar_por: str, filtros: dict) -> str:
    """Retorna a data mais recente disponível no conjunto filtrado."""

    query = select(func.max(base.c.data_atualizacao)).select_from(base)
    query = _aplicar_filtros(query, base, comparar_por, filtros)
    return _formatar_data_br(db.execute(query).scalar())


def obter_distribuicao(
    db: Session,
    comparar_por: str,
    estado: str | None = None,
    partido: str | None = None,
    genero: str | None = None,
    mes: int | None = None,
) -> dict:
    """Orquestra todos os cálculos exigidos por GET /api/graficos/distribuicao."""

    base = _base_proposicoes()
    filtros = {"estado": estado, "partido": partido,
               "genero": genero, "mes": mes}

    return {
        "comparar_por": comparar_por,
        "data_atualizacao": _data_atualizacao(db, base, comparar_por, filtros),
        "indicadores": {
            "total_pls": _total_pls(db, base, comparar_por, filtros),
            "partido_mais_ativo": _mais_ativo(db, base, comparar_por, filtros, "partido"),
            "estado_mais_ativo": _mais_ativo(db, base, comparar_por, filtros, "estado"),
        },
        "dados": _agregar_por_dimensao(db, base, comparar_por, filtros),
    }


def obter_resumo(db: Session) -> dict:
    from app.models import TramitacaoCamara, TramitacaoSenado
    from datetime import datetime

    # 1. Tempo Médio (Apenas Sancionados)
    query_camara = db.execute(
        select(PlCamara.data_apresentacao, func.max(
            TramitacaoCamara.data_tramitacao))
        .outerjoin(TramitacaoCamara, TramitacaoCamara.id_pl == PlCamara.id)
        .where(PlCamara.descricao_situacao == "Transformado em Norma Jurídica")
        .group_by(PlCamara.id)
    ).all()

    query_senado = db.execute(
        select(PlSenado.data_apresentacao, func.max(
            TramitacaoSenado.data_tramitacao))
        .outerjoin(TramitacaoSenado, TramitacaoSenado.id_pl == PlSenado.id)
        .where(PlSenado.dados_raw['situacaoAtual'].astext.in_(['TNJR', 'TNJRVETO']))
        .group_by(PlSenado.id)
    ).all()

    soma_dias = 0
    total_pls_tempo = 0
    hoje = datetime.now()

    for dt_apresentacao, max_tramitacao in query_camara + query_senado:
        if not dt_apresentacao:
            continue
        dt_fim = max_tramitacao or hoje

        dt_a = dt_apresentacao.date() if isinstance(
            dt_apresentacao, datetime) else dt_apresentacao
        dt_f = dt_fim.date() if isinstance(dt_fim, datetime) else dt_fim

        dias = max(0, (dt_f - dt_a).days)
        soma_dias += dias
        total_pls_tempo += 1

    dias_medios = soma_dias // total_pls_tempo if total_pls_tempo else 0

    # 2. Top Estados
    base = _base_proposicoes()
    query_estados = select(
        func.upper(base.c.estado).label("uf"),
        func.count(func.distinct(base.c.proposicao_id)).label("total_pls")
    ).where(base.c.estado.isnot(None), base.c.estado != "").group_by(func.upper(base.c.estado)).order_by(func.count(func.distinct(base.c.proposicao_id)).desc()).limit(5)

    mapa_estados = {
        "AC": "Acre", "AL": "Alagoas", "AP": "Amapá", "AM": "Amazonas", "BA": "Bahia", "CE": "Ceará", "DF": "Distrito Federal",
        "ES": "Espírito Santo", "GO": "Goiás", "MA": "Maranhão", "MT": "Mato Grosso", "MS": "Mato Grosso do Sul",
        "MG": "Minas Gerais", "PA": "Pará", "PB": "Paraíba", "PR": "Paraná", "PE": "Pernambuco", "PI": "Piauí",
        "RJ": "Rio de Janeiro", "RN": "Rio Grande do Norte", "RS": "Rio Grande do Sul", "RO": "Rondônia", "RR": "Roraima",
        "SC": "Santa Catarina", "SP": "São Paulo", "SE": "Sergipe", "TO": "Tocantins"
    }

    top_estados = []
    for row in db.execute(query_estados).all():
        top_estados.append({
            "estado": mapa_estados.get(row.uf, row.uf),
            "uf": row.uf,
            "total_pls": row.total_pls
        })

    # 3. Parlamentares Ativos
    camara_parl = select(
        Parlamentar.nome_eleitoral.label("nome"),
        Parlamentar.sigla_partido.label("partido"),
        Parlamentar.sigla_uf.label("uf"),
        Parlamentar.sexo.label("sexo"),
        literal("Câmara").label("casa"),
        func.count(func.distinct(AutoriaCamara.id_pl)).label("total")
    ).join(AutoriaCamara, AutoriaCamara.id_parlamentar == Parlamentar.id).group_by(Parlamentar.id)

    senado_parl = select(
        Parlamentar.nome_eleitoral.label("nome"),
        Parlamentar.sigla_partido.label("partido"),
        Parlamentar.sigla_uf.label("uf"),
        Parlamentar.sexo.label("sexo"),
        literal("Senado").label("casa"),
        func.count(func.distinct(AutoriaSenado.id_pl)).label("total")
    ).join(AutoriaSenado, AutoriaSenado.id_parlamentar == Parlamentar.id).group_by(Parlamentar.id)

    query_parl = camara_parl.union_all(senado_parl).subquery()
    query_top_parl = select(
        query_parl.c.nome, query_parl.c.partido, query_parl.c.uf, query_parl.c.sexo, query_parl.c.casa, func.sum(
            query_parl.c.total).label("total_propostas")
    ).group_by(query_parl.c.nome, query_parl.c.partido, query_parl.c.uf, query_parl.c.sexo, query_parl.c.casa).order_by(func.sum(query_parl.c.total).desc()).limit(3)

    parlamentares = []
    for row in db.execute(query_top_parl).all():
        cargo = "Deputado Federal" if row.casa == "Câmara" and row.sexo == "M" else "Deputada Federal" if row.casa == "Câmara" else "Senador" if row.sexo == "M" else "Senadora"
        nomes = row.nome.split()
        iniciais = (nomes[0][0] + nomes[1][0]
                    ).upper() if len(nomes) > 1 else nomes[0][0:2].upper()

        parlamentares.append({
            "nome": row.nome,
            "iniciais": iniciais,
            "descricao": f"{cargo} - {row.partido}",
            "uf": row.uf,
            "total_propostas": row.total_propostas
        })

    return {
        "tempo_medio_tramitacao": {
            "dias": dias_medios
        },
        "top_estados": top_estados,
        "parlamentares_ativos": parlamentares
    }
