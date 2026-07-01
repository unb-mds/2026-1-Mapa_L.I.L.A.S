from app.services import collector


class DummySession:
    def __init__(self):
        self.commits = 0

    def commit(self):
        self.commits += 1


def test_coletar_camara_ignores_projects_authored_by_senado(mocker):
    session = DummySession()
    mocker.patch.object(collector.camara_client, "SIGLAS_TIPO", ["PL"])
    mocker.patch.object(collector.camara_client, "PALAVRAS_CHAVE", ["mulher"])
    mocker.patch.object(
        collector.camara_client,
        "listar_proposicoes",
        return_value=iter([{"id": 1}]),
    )
    mocker.patch.object(
        collector.camara_client,
        "buscar_autores",
        return_value=[{"nome": "Senado Federal - Autor"}],
    )
    upsert = mocker.patch("app.services.collector.upsert_pl_camara")

    total = collector.coletar_camara(session)

    assert total == 0
    assert session.commits == 0
    upsert.assert_not_called()


def test_coletar_camara_enriches_authors_and_commits(mocker):
    session = DummySession()
    autor = {
        "nome": "Deputada Teste",
        "uri": "https://dadosabertos.camara.leg.br/api/v2/deputados/123",
    }
    mocker.patch.object(collector.camara_client, "SIGLAS_TIPO", ["PL"])
    mocker.patch.object(collector.camara_client, "PALAVRAS_CHAVE", ["mulher"])
    mocker.patch("app.services.collector.get_dynamic_keywords", return_value=["mulher"])
    mocker.patch.object(
        collector.camara_client,
        "listar_proposicoes",
        return_value=iter([{"id": 1}]),
    )
    mocker.patch.object(collector.camara_client, "buscar_autores", return_value=[autor])
    mocker.patch.object(collector.camara_client, "buscar_detalhe", return_value={"id": 1})
    mocker.patch.object(
        collector.camara_client,
        "buscar_deputado",
        return_value={"sexo": "F"},
    )
    mocker.patch.object(collector.camara_client, "buscar_tramitacoes", return_value=[])
    mocker.patch("app.services.collector.upsert_pl_camara", return_value=1)
    upsert_autores = mocker.patch("app.services.collector.upsert_autores_camara")
    upsert_tramitacoes = mocker.patch("app.services.collector.upsert_tramitacoes_camara")

    total = collector.coletar_camara(session)

    assert total == 1
    assert session.commits == 1
    assert autor["detalhes_deputado"] == {"sexo": "F"}
    upsert_autores.assert_called_once_with(session, 1, [autor])
    upsert_tramitacoes.assert_called_once_with(session, 1, [])


def test_coletar_senado_ignores_projects_authored_by_camara(mocker):
    session = DummySession()
    mocker.patch.object(collector.senado_client, "SIGLAS_TIPO", ["PL"])
    mocker.patch.object(collector.senado_client, "PALAVRAS_CHAVE", ["mulher"])
    mocker.patch.object(
        collector.senado_client,
        "pesquisar_materias",
        return_value=[
            {
                "id": 1,
                "identificacao": "PL 1/2026",
                "autoria": "C\u00e2mara dos Deputados",
            }
        ],
    )
    upsert = mocker.patch("app.services.collector.upsert_pl_senado")

    total = collector.coletar_senado(session)

    assert total == 0
    assert session.commits == 0
    upsert.assert_not_called()


def test_coletar_senado_fetches_detail_and_commits(mocker):
    session = DummySession()
    detalhe = {"autoria": "Senadora Teste"}
    mocker.patch.object(collector.senado_client, "SIGLAS_TIPO", ["PL"])
    mocker.patch.object(collector.senado_client, "PALAVRAS_CHAVE", ["mulher"])
    mocker.patch("app.services.collector.get_dynamic_keywords", return_value=["mulher"])
    pesquisar = mocker.patch.object(
        collector.senado_client,
        "pesquisar_materias",
        return_value=[{"id": 1, "identificacao": "PL 1/2026", "autoria": "Senadora"}],
    )
    mocker.patch("app.services.collector.upsert_pl_senado", return_value=1)
    mocker.patch.object(collector.senado_client, "buscar_detalhe", return_value=detalhe)
    upsert_autores = mocker.patch("app.services.collector.upsert_autores_senado")
    upsert_tramitacoes = mocker.patch("app.services.collector.upsert_tramitacoes_senado")

    total = collector.coletar_senado(session, ano_inicial=2024, numdias=2)

    assert total == 1
    assert session.commits == 1
    pesquisar.assert_called_once_with(
        keyword="mulher",
        sigla_tipo="PL",
        ano_inicial=2024,
        numdias=2,
    )
    upsert_autores.assert_called_once_with(session, 1, detalhe)
    upsert_tramitacoes.assert_called_once_with(session, 1, detalhe)
