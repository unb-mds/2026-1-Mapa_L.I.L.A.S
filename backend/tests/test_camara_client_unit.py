import requests

from app.services import camara_client


class DummyResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_get_returns_json_and_uses_expected_request_options(mocker):
    get = mocker.patch(
        "app.services.camara_client.requests.get",
        return_value=DummyResponse({"dados": [{"id": 1}]}),
    )

    result = camara_client._get("/proposicoes", {"pagina": 1})

    assert result == {"dados": [{"id": 1}]}
    get.assert_called_once_with(
        f"{camara_client.BASE_URL}/proposicoes",
        params={"pagina": 1},
        timeout=camara_client.TIMEOUT,
    )


def test_get_returns_none_when_request_fails(mocker):
    mocker.patch(
        "app.services.camara_client.requests.get",
        side_effect=requests.exceptions.Timeout("timeout"),
    )

    assert camara_client._get("/proposicoes") is None


def test_listar_proposicoes_paginates_and_stops_without_next_link(mocker):
    calls = []

    def fake_get(path, params):
        calls.append((path, params.copy()))
        if params["pagina"] == 1:
            return {"dados": [{"id": 1}], "links": [{"rel": "next"}]}
        return {"dados": [{"id": 2}], "links": []}

    mocker.patch("app.services.camara_client._get", side_effect=fake_get)

    result = list(camara_client.listar_proposicoes("PL", "direitos da mulher", 2024))

    assert result == [{"id": 1}, {"id": 2}]
    assert [params["pagina"] for _, params in calls] == [1, 2]
    assert all(params["siglaTipo"] == "PL" for _, params in calls)
    assert all(params["dataApresentacaoInicio"] == "2024-01-01" for _, params in calls)


def test_listar_proposicoes_sends_configured_keywords(mocker):
    captured_params = []

    def fake_get(path, params):
        captured_params.append(params.copy())
        return {"dados": [{"id": 1}], "links": []}

    mocker.patch("app.services.camara_client._get", side_effect=fake_get)

    list(camara_client.listar_proposicoes("PL", "direitos da mulher"))

    assert captured_params[0]["keywords"] == camara_client.PALAVRAS_CHAVE


def test_buscar_deputado_uses_cache(mocker):
    camara_client._cache_deputados.clear()
    get = mocker.patch(
        "app.services.camara_client._get",
        return_value={"dados": {"id": 123, "nome": "Deputada Teste"}},
    )

    first = camara_client.buscar_deputado(123)
    second = camara_client.buscar_deputado(123)

    assert first == {"id": 123, "nome": "Deputada Teste"}
    assert second == first
    get.assert_called_once_with("/deputados/123")
