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
            func.concat(literal("camara:"), cast(PlCamara.id, String)).label("proposicao_id"),
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
            func.concat(literal("senado:"), cast(PlSenado.id, String)).label("proposicao_id"),
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
        query = query.where(cast(func.extract("month", base.c.data_apresentacao), Integer) == mes)

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

    query = select(label_col, func.count(func.distinct(base.c.proposicao_id)).label("total")).select_from(base)
    query = _aplicar_filtros(query, base, comparar_por, filtros)
    query = _aplicar_label_preenchido(query, label_col, comparar_por)
    query = query.group_by(label_col).order_by(func.count(func.distinct(base.c.proposicao_id)).desc())

    dados = []
    for row in db.execute(query).all():
        label = _label_resposta(comparar_por, row.label)
        if label:
            dados.append({"label": label, "total": row.total})
    return dados


def _total_pls(db: Session, base, comparar_por: str, filtros: dict) -> int:
    """Calcula o total de registros considerados após os filtros válidos."""

    query = select(func.count(func.distinct(base.c.proposicao_id))).select_from(base)
    query = _aplicar_filtros(query, base, comparar_por, filtros)
    return db.execute(query).scalar() or 0


def _mais_ativo(db: Session, base, comparar_por: str, filtros: dict, campo: str) -> str | None:
    """Calcula o partido ou estado com mais propostas após os filtros."""

    label_col = func.upper(getattr(base.c, campo)).label("label")
    query = select(label_col, func.count(func.distinct(base.c.proposicao_id)).label("total")).select_from(base)
    query = _aplicar_filtros(query, base, comparar_por, filtros)
    query = query.where(label_col.isnot(None), label_col != "")
    query = query.group_by(label_col).order_by(func.count(func.distinct(base.c.proposicao_id)).desc()).limit(1)

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
    filtros = {"estado": estado, "partido": partido, "genero": genero, "mes": mes}

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
