from datetime import date

from app.models import (
    AutoriaCamara,
    AutoriaSenado,
    Parlamentar,
    PlCamara,
    PlSenado,
    TramitacaoSenado,
)
from app.services import normalizer


class FakeQuery:
    def filter(self, *args, **kwargs):
        return self
    def first(self):
        return None

class FakeSession:
    def __init__(self):
        self.merged = []

    def merge(self, obj):
        self.merged.append(obj)
        return obj

    def add(self, obj):
        self.merged.append(obj)

    def query(self, *args, **kwargs):
        return FakeQuery()


def merged_of(session, model):
    return [obj for obj in session.merged if isinstance(obj, model)]


def test_helpers_normalize_common_payload_shapes():
    assert normalizer.limpar_sexo(None) == "M"
    assert normalizer.limpar_sexo(" feminino ") == "F"
    assert normalizer.limpar_sexo("x") == "M"
    assert normalizer.extrair_lista_camara({"dados": [{"id": 1}]}) == [{"id": 1}]
    assert normalizer.extrair_lista_camara("invalido") == []
    assert normalizer.extrair_dict_camara([{"id": 2}]) == {"id": 2}
    assert normalizer.garantir_lista({"id": 3}) == [{"id": 3}]
    assert normalizer.navegar_seguro({"a": [{"b": "valor"}]}, ["a", "b"]) == "valor"


def test_upsert_pl_camara_uses_detail_status_and_raw_payload():
    session = FakeSession()
    item = {"id": 100, "numero": 10, "ano": 2026, "siglaTipo": "PL"}
    detalhe = {
        "dados": {
            "id": 100,
            "numero": 10,
            "ano": 2026,
            "siglaTipo": "PL",
            "uri": "https://camara/pl/100",
            "dataApresentacao": "2026-01-01T00:00:00",
            "ementa": "Protecao as mulheres",
            "descricaoTipo": "Projeto de Lei",
            "statusProposicao": [
                {"descricaoSituacao": "Arquivada", "despacho": "Despacho"}
            ],
        }
    }

    result = normalizer.upsert_pl_camara(
        session,
        item,
        detalhe,
        {"captured_at": date(2026, 1, 1)},
    )

    assert result == 100
    pl = merged_of(session, PlCamara)[0]
    assert pl.id == 100
    assert pl.descricao_situacao == "Arquivada"
    assert pl.despacho == "Despacho"
    assert pl.dados_raw == {"captured_at": "2026-01-01"}


def test_upsert_autores_camara_creates_parlamentar_and_autoria():
    session = FakeSession()
    autores = {
        "dados": [
            {
                "uri": "https://dadosabertos.camara.leg.br/api/v2/deputados/123",
                "nome": "Deputada Teste",
                "tipo": "Autor",
                "detalhes_deputado": {
                    "sexo": "F",
                    "ultimoStatus": {
                        "nomeEleitoral": "Dep. Teste",
                        "siglaPartido": "ABC",
                        "siglaUf": "DF",
                        "urlFoto": "foto.jpg",
                        "situacao": "Exercicio",
                    },
                },
            },
            {"nome": "Sem URI"},
        ]
    }

    normalizer.upsert_autores_camara(session, 100, autores)

    parlamentar = merged_of(session, Parlamentar)[0]
    autoria = merged_of(session, AutoriaCamara)[0]
    assert parlamentar.id == "cam_123"
    assert parlamentar.nome_eleitoral == "Dep. Teste"
    assert parlamentar.sexo == "F"
    assert autoria.id_pl == 100
    assert autoria.id_parlamentar == "cam_123"


def test_upsert_pl_senado_reads_nested_fields():
    session = FakeSession()
    item = {
        "id": 200,
        "codigoMateria": 300,
        "identificacao": "PL 20/2026",
        "conteudo": {"ementa": "Ementa Senado", "tipo": "Normativo"},
        "documento": {"dataApresentacao": "2026-02-01", "tipo": "Projeto"},
        "deliberacao": {"data": "2026-03-01", "siglaTipo": "SAN"},
        "tramitando": "Sim",
    }

    result = normalizer.upsert_pl_senado(session, item, item)

    assert result == 200
    pl = merged_of(session, PlSenado)[0]
    assert pl.codigo_materia == 300
    assert pl.ementa == "Ementa Senado"
    assert pl.tramitando is True
    assert pl.sigla_tipo_deliberacao == "SAN"


def test_upsert_autores_senado_supports_string_autoria_fallback():
    session = FakeSession()

    normalizer.upsert_autores_senado(session, 200, {"autoria": "Senadora Teste"})

    parlamentar = merged_of(session, Parlamentar)[0]
    autoria = merged_of(session, AutoriaSenado)[0]
    assert parlamentar.id == "sen_str_200"
    assert parlamentar.casa == "Senado"
    assert parlamentar.nome_eleitoral == "Senadora Teste"
    assert autoria.id_parlamentar == "sen_str_200"


def test_upsert_tramitacoes_senado_prefers_informes_legislativos():
    session = FakeSession()
    payload = {
        "autuacoes": [
            {
                "informesLegislativos": [
                    {
                        "data": "2026-04-01",
                        "siglaSituacaoIniciada": "TRAM",
                        "descricao": "Recebido",
                        "enteAdministrativo": {"sigla": "CDH"},
                        "id": 7,
                    }
                ]
            }
        ],
        "movimentacoes": [{"id": 99}],
    }

    normalizer.upsert_tramitacoes_senado(session, 200, payload)

    tramitacao = merged_of(session, TramitacaoSenado)[0]
    assert tramitacao.id_pl == 200
    assert tramitacao.sequencia == 7
    assert tramitacao.local == "CDH"
    assert tramitacao.descricao == "Recebido"


def test_status_normalizers_return_frontend_values():
    assert normalizer.normalizar_status_camara(None) == "em_tramitacao"
    assert normalizer.normalizar_status_camara("Arquivada") == "arquivado"
    assert normalizer.normalizar_status_senado("SAN", True) == "em_tramitacao"
    assert normalizer.normalizar_status_senado("ARQUIVADO_FIM_LEGISLATURA", False) == "arquivado"
