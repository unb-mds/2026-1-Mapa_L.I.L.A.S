"""
app/services/normalizer.py

Normalizador de dados: Transforma os payloads brutos da Câmara e do Senado
em registros do banco de dados (Tabelas de PLs, Autores e Tramitações).
"""

import json
import logging
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models import PlCamara, PlSenado, AutoriaCamara, AutoriaSenado, TramitacaoCamara, TramitacaoSenado, Parlamentar

logger = logging.getLogger(__name__)


def higienizar_para_jsonb(dados: Any) -> Any:
    if dados is None:
        return None
    return json.loads(json.dumps(dados, default=str))


def limpar_sexo(raw_sexo: Any) -> str:
    """Garante que o sexo será sempre 'M' ou 'F' (1 caractere) para o banco."""
    if not raw_sexo:
        return "M"
    letra = str(raw_sexo).strip().upper()[0]
    return letra if letra in ["M", "F"] else "M"

# ---------------------------------------------------------------------------
# UPSERTS DA CÂMARA DOS DEPUTADOS
# ---------------------------------------------------------------------------


def extrair_lista_camara(payload: Any) -> List[Dict]:
    if isinstance(payload, dict):
        return payload.get("dados", [])
    elif isinstance(payload, list):
        return payload
    return []


def extrair_dict_camara(payload: Any) -> Dict:
    if isinstance(payload, dict):
        return payload.get("dados", payload)
    elif isinstance(payload, list) and len(payload) > 0:
        return payload[0] if isinstance(payload[0], dict) else {}
    return {}


def upsert_pl_camara(session: Session, item_raw: Dict, detalhe_raw: Optional[Dict], dados_originais: Dict) -> Optional[int]:
    try:
        raw_limpo = higienizar_para_jsonb(dados_originais)
        item = extrair_dict_camara(item_raw)
        detalhe = extrair_dict_camara(detalhe_raw) if detalhe_raw else {}

        pl_id = item.get("id")
        if not pl_id:
            return None

        proposicao = detalhe if detalhe else item
        status_info = proposicao.get("statusProposicao", {})
        if isinstance(status_info, list):
            status_info = status_info[0] if status_info else {}

        nova_pl = PlCamara(
            id=int(pl_id),
            numero=int(proposicao.get("numero", 0)),
            ano=int(proposicao.get("ano")) if proposicao.get("ano") else None,
            sigla_tipo=proposicao.get("siglaTipo"),
            uri=proposicao.get("uri"),
            data_apresentacao=proposicao.get("dataApresentacao"),
            ementa=proposicao.get("ementa", ""),
            descricao_tipo=proposicao.get("descricaoTipo"),
            descricao_situacao=status_info.get("descricaoSituacao"),
            despacho=status_info.get("despacho"),
            dados_raw=raw_limpo
        )
        session.merge(nova_pl)
        return int(pl_id)
    except Exception as exc:
        logger.error("Erro no upsert_pl_camara: %s", exc)
        return None


def upsert_autores_camara(session: Session, id_pl: int, autores_raw: Any) -> None:
    try:
        autores_limpos = higienizar_para_jsonb(autores_raw)
        lista_autores = extrair_lista_camara(autores_limpos)

        for autor in lista_autores:
            if not isinstance(autor, dict):
                continue

            uri = autor.get("uri")
            if not uri:
                continue

            try:
                parl_id_api = uri.rstrip("/").split("/")[-1]
                parlamentar_id = f"cam_{parl_id_api}"
            except Exception:
                continue

            detalhes = autor.get("detalhes_deputado", {})
            ultimo_status = detalhes.get("ultimoStatus", {})

            parlamentar = Parlamentar(
                id=parlamentar_id,
                casa="Câmara",
                nome_eleitoral=ultimo_status.get(
                    "nomeEleitoral") or autor.get("nome"),
                sigla_partido=ultimo_status.get("siglaPartido", ""),
                sigla_uf=ultimo_status.get("siglaUf", ""),
                # Correção aplicada
                sexo=limpar_sexo(detalhes.get("sexo")),
                url_foto=ultimo_status.get("urlFoto", ""),
                status_mandato=ultimo_status.get("situacao", "Desconhecido")
            )
            session.merge(parlamentar)

            autoria = AutoriaCamara(
                id_pl=id_pl,
                id_parlamentar=parlamentar_id,
                tipo_autoria=autor.get("tipo")
            )
            session.merge(autoria)

    except Exception as exc:
        logger.error(
            "Erro no upsert_autores_camara para o PL %d: %s", id_pl, exc)


def upsert_tramitacoes_camara(session: Session, id_pl: int, tramitacoes_raw: Any) -> None:
    try:
        tramitacoes_limpas = higienizar_para_jsonb(tramitacoes_raw)
        lista_tramitacoes = extrair_lista_camara(tramitacoes_limpas)

        for tramitacao in lista_tramitacoes:
            if not isinstance(tramitacao, dict):
                continue

            seq = tramitacao.get("sequencia")
            data_t = tramitacao.get("dataHora")

            # Busca se já existe uma tramitação igual
            query = session.query(TramitacaoCamara).filter(
                TramitacaoCamara.id_pl == id_pl)
            if seq is not None:
                query = query.filter(TramitacaoCamara.sequencia == seq)
            elif data_t is not None:
                query = query.filter(
                    TramitacaoCamara.data_tramitacao == data_t)

            existente = query.first()

            if existente:
                # Atualiza
                existente.situacao = tramitacao.get("descricaoSituacao")
                existente.descricao = tramitacao.get("descricaoTramitacao")
                existente.local = tramitacao.get("siglaOrgao")
                existente.dados_raw = tramitacao
            else:
                # Insere nova
                nova_tramitacao = TramitacaoCamara(
                    id_pl=id_pl,
                    data_tramitacao=data_t,
                    situacao=tramitacao.get("descricaoSituacao"),
                    descricao=tramitacao.get("descricaoTramitacao"),
                    local=tramitacao.get("siglaOrgao"),
                    sequencia=seq,
                    dados_raw=tramitacao
                )
                session.add(nova_tramitacao)

    except Exception as exc:
        logger.error(
            "Erro no upsert_tramitacoes_camara para o PL %d: %s", id_pl, exc)

# ---------------------------------------------------------------------------
# UPSERTS DO SENADO FEDERAL
# ---------------------------------------------------------------------------


def navegar_seguro(payload: Any, caminho: List[str]) -> Any:
    atual = payload
    for chave in caminho:
        if isinstance(atual, list):
            atual = atual[0] if atual else {}
        if isinstance(atual, dict):
            atual = atual.get(chave, {})
        else:
            return {}
    return atual


def garantir_lista(payload: Any) -> List[Any]:
    if not payload or payload == {}:
        return []
    if isinstance(payload, list):
        return payload
    return [payload]


def upsert_pl_senado(session: Session, item_raw: Any, dados_originais: Any) -> Optional[int]:
    try:
        raw_limpo = higienizar_para_jsonb(dados_originais)

        if isinstance(item_raw, list):
            item_raw = item_raw[0] if item_raw else {}
        if not isinstance(item_raw, dict):
            return None

        id_materia = item_raw.get("id")
        if not id_materia:
            return None

        conteudo = item_raw.get("conteudo", {})
        documento = item_raw.get("documento", {})
        deliberacao = item_raw.get("deliberacao", {})

        nova_pl = PlSenado(
            id=int(id_materia),
            codigo_materia=int(item_raw.get("codigoMateria", 0)),
            identificacao=item_raw.get("identificacao", ""),
            data_apresentacao=documento.get(
                "dataApresentacao") or item_raw.get("dataApresentacao"),
            data_deliberacao=deliberacao.get(
                "data") or item_raw.get("dataDeliberacao"),
            ementa=conteudo.get("ementa") or item_raw.get("ementa", ""),
            objetivo=conteudo.get("tipo") or item_raw.get("objetivo"),
            tipo_documento=documento.get(
                "tipo") or item_raw.get("tipoDocumento"),
            tramitando=True if item_raw.get("tramitando") == "Sim" else False,
            sigla_tipo_deliberacao=deliberacao.get(
                "siglaTipo") or item_raw.get("siglaTipoDeliberacao"),
            dados_raw=raw_limpo
        )
        session.merge(nova_pl)
        return int(id_materia)
    except Exception as exc:
        logger.error("Erro no upsert_pl_senado: %s", exc)
        return None


def upsert_autores_senado(session: Session, id_pl: int, detalhe_raw: Any) -> None:
    try:
        raw_limpo = higienizar_para_jsonb(detalhe_raw)

        nodo_autores = (
            raw_limpo.get("autoriaIniciativa") or
            raw_limpo.get("documento", {}).get("autoria") or
            raw_limpo.get("autores") or
            raw_limpo.get("autorias") or
            navegar_seguro(raw_limpo, ["Processo", "Autoria", "Autor"]) or
            navegar_seguro(raw_limpo, ["Materia", "Autoria", "Autor"])
        )

        lista_autores = garantir_lista(nodo_autores)

        if not lista_autores and isinstance(raw_limpo.get("autoria"), str):
            nome_autor = raw_limpo.get("autoria")
            parlamentar_id = f"sen_str_{id_pl}"

            parlamentar = Parlamentar(
                id=parlamentar_id, casa="Senado", nome_eleitoral=nome_autor,
                sigla_partido="", sexo="M"
            )
            session.merge(parlamentar)
            autoria = AutoriaSenado(
                id_pl=id_pl, id_parlamentar=parlamentar_id, tipo_autoria="Autor Principal")
            session.merge(autoria)
            return

        for autor_raw in lista_autores:
            if not isinstance(autor_raw, dict):
                continue

            parl_info = autor_raw.get("IdentificacaoParlamentar") or autor_raw.get(
                "parlamentar") or autor_raw
            if isinstance(parl_info, list):
                parl_info = parl_info[0] if parl_info else {}

            parl_id_api = parl_info.get("codigoParlamentar") or parl_info.get(
                "CodigoParlamentar") or parl_info.get("codigo") or parl_info.get("id")
            if not parl_id_api:
                continue

            parlamentar_id = f"sen_{parl_id_api}"

            detalhes_extra = autor_raw.get("detalhes_senador", {})
            parl_detalhe = navegar_seguro(
                detalhes_extra, ["DetalheParlamentar", "Parlamentar", "IdentificacaoParlamentar"])

            # Captura o sexo bruto de onde ele estiver e passa pelo filtro
            raw_sexo = parl_detalhe.get(
                "SexoParlamentar") or parl_info.get("sexo")

            parlamentar = Parlamentar(
                id=parlamentar_id,
                casa="Senado",
                nome_eleitoral=parl_detalhe.get("NomeParlamentar") or parl_info.get(
                    "autor") or parl_info.get("nome") or "Desconhecido",
                sigla_partido=parl_detalhe.get(
                    "SiglaPartidoParlamentar") or parl_info.get("siglaPartido") or "",
                sigla_uf=parl_detalhe.get("uf") or parl_info.get("uf") or "",
                # Correção aplicada
                sexo=limpar_sexo(raw_sexo),
                url_foto=parl_detalhe.get("UrlFotoParlamentar") or "",
                status_mandato=parl_detalhe.get(
                    "DescricaoParticipacao") or "Exercício"
            )

            session.merge(parlamentar)

            autoria = AutoriaSenado(
                id_pl=id_pl,
                id_parlamentar=parlamentar_id,
                tipo_autoria=autor_raw.get("descricaoTipo") or autor_raw.get(
                    "DescricaoTipoAutoria") or autor_raw.get("tipo") or "Autor"
            )
            session.merge(autoria)

    except Exception as exc:
        logger.error(
            "Erro no upsert_autores_senado para o PL %d: %s", id_pl, exc)


def upsert_tramitacoes_senado(session: Session, id_pl: int, movimentacoes_raw: Any) -> None:
    try:
        raw_limpo = higienizar_para_jsonb(movimentacoes_raw)

        autuacoes = raw_limpo.get("autuacoes", [])
        informes_legislativos = []
        if isinstance(autuacoes, list) and len(autuacoes) > 0:
            for autuacao in autuacoes:
                if isinstance(autuacao, dict):
                    informes_legislativos.extend(
                        autuacao.get("informesLegislativos", []))

        nodo_tramitacoes = (
            informes_legislativos or
            raw_limpo.get("movimentacoes") or
            raw_limpo.get("andamentos") or
            raw_limpo.get("tramitacoes") or
            navegar_seguro(raw_limpo, ["Processo", "Movimentacoes", "Movimentacao"]) or
            navegar_seguro(
                raw_limpo, ["Materia", "Movimentacoes", "Movimentacao"])
        )

        lista_tramitacoes = garantir_lista(nodo_tramitacoes)

        for idx, tramitacao in enumerate(lista_tramitacoes):
            if not isinstance(tramitacao, dict):
                continue

            ente_admin = tramitacao.get("enteAdministrativo", {})
            local_nome = ente_admin.get("nome") or ente_admin.get("sigla") or tramitacao.get(
                "DescricaoLocal") or tramitacao.get("local") or tramitacao.get("orgao")

            seq = tramitacao.get("id") or tramitacao.get(
                "SequenciaMovimentacao") or tramitacao.get("sequencia") or (idx + 1)
            data_t = tramitacao.get("data") or tramitacao.get(
                "DataMovimentacao") or tramitacao.get("dataHora")

            # Busca se já existe uma tramitação igual
            query = session.query(TramitacaoSenado).filter(
                TramitacaoSenado.id_pl == id_pl)
            if seq is not None:
                query = query.filter(TramitacaoSenado.sequencia == seq)
            elif data_t is not None:
                query = query.filter(
                    TramitacaoSenado.data_tramitacao == data_t)

            existente = query.first()

            if existente:
                existente.situacao = tramitacao.get("siglaSituacaoIniciada") or tramitacao.get(
                    "DescricaoMovimentacao") or tramitacao.get("situacao") or "Informação"
                existente.descricao = tramitacao.get("descricao") or tramitacao.get(
                    "DescricaoMovimentacao") or tramitacao.get("texto")
                existente.local = local_nome
                existente.dados_raw = tramitacao
            else:
                nova_tramitacao = TramitacaoSenado(
                    id_pl=id_pl,
                    data_tramitacao=data_t,
                    situacao=tramitacao.get("siglaSituacaoIniciada") or tramitacao.get(
                        "DescricaoMovimentacao") or tramitacao.get("situacao") or "Informação",
                    descricao=tramitacao.get("descricao") or tramitacao.get(
                        "DescricaoMovimentacao") or tramitacao.get("texto"),
                    local=local_nome,
                    sequencia=seq,
                    dados_raw=tramitacao
                )
                session.add(nova_tramitacao)

    except Exception as exc:
        logger.error(
            "Erro no upsert_tramitacoes_senado para o PL %d: %s", id_pl, exc)


def normalizar_status_camara(descricao_situacao: Optional[str]) -> str:
    """
    Converte descricao_situacao da Câmara nos 3 valores aceitos pelo front end.
    """
    if not descricao_situacao:
        return "em_tramitacao"
    if descricao_situacao == "Transformado em Norma Jurídica":
        return "aprovado"
    if descricao_situacao == "Arquivada":
        return "arquivado"
    return "em_tramitacao"


def normalizar_status_senado(situacao_atual: Optional[str], tramitando: Optional[bool] = None) -> str:
    """
    Converte situacao_atual do Senado nos 3 valores aceitos pelo front end.
    """
    if not situacao_atual:
        return "arquivado"
    situacao_atual = situacao_atual.upper()
    if situacao_atual in ("TNJR", "TNJRVETO"):
        return "aprovado"
    if situacao_atual in ("ARQVD", "ARQV_CD", "PRJDA", "RJTDA", "RTPA", "ARQUIVADO_FIM_LEGISLATURA"):
        return "arquivado"
    return "em_tramitacao"
